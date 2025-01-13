import io
import json

import openai
from fastapi import HTTPException,UploadFile
from dotenv import load_dotenv
from app.models.feedback import Feedback
from sqlalchemy.orm import Session
import os

# .env 파일 로드
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

# Whisper (STT)
def transcribe_audio(file: UploadFile) -> str:
    try:
        file.file.seek(0)
        file_content = io.BytesIO(file.file.read())
        file_content.name = file.filename  # 파일 이름 설정 (필수)
        response = openai.Audio.transcribe(
            model="whisper-1",
            file=file_content
        )

        # 변환된 텍스트 반환
        return response["text"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"STT 변환 실패: {str(e)}")

def get_gpt_response_limited(prompt: str, messages: list) -> str:
    messages.append({
        "role": "user",
        "content": f"Please respond in English only and keep your response within 30 words. Here is the prompt: {prompt}"
    })
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GPT 응답 생성 실패: {str(e)}")

def get_grammar_feedback(prompt: str, messages: list) -> str:
    messages.append({
        "role": "user",
        "content": f"다음 문장의 문법적 정확성을 분석하고, 문제가 있다면 교정 후 제안해 주세요. 또한 설명을 한국어로 친절하게 작성해 주세요: '{prompt}'"
    })
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"문법 피드백 생성 실패: {str(e)}")

"""
def get_pronunciation_feedback(azure_response: str, messages: list ) -> str:
    messages.append({
        "role": "user",
        "content": (
            "Here is the pronunciation assessment data from Azure. "
            "Provide feedback within 30 words:\n\n"
            f"{json.dumps(azure_response)}"
        )
    })
    # 2) GPT 호출
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages)  # GPT 호출
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate GPT feedback: {str(e)}")
    """

async def get_pronunciation_feedback(azure_response: dict) -> str:
    # Azure 결과를 문자열로 변환
    azure_response_str = "\n".join(
        f"{key}: {value}" for key, value in azure_response.items()
    )

    # GPT 요청 메시지 구성
    messages = [
        {
            "role": "user",
            "content": (
                f"다음 데이터는 Azure의 발음 평가 결과입니다:\n\n{azure_response_str}\n\n"
                "이 문장들의 결과를 토대로 내가 어디 단어가 문제이고 어디 발음이 문제인지 발음결과토대로 요약해서 핵심만 알려줘 "
                "친절한 한국어로 작성해주세요."
            )
        }
    ]

    try:
        response = await openai.ChatCompletion.acreate(  # 비동기 호출로 변경
            model="gpt-4",
            messages=messages
        )
        return response["choices"][0]["message"]["content"]

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate GPT feedback: {str(e)}"
        )
