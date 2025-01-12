from fastapi import APIRouter, Depends, UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.config.azure.pronunciation_feedback import analyze_pronunciation_with_azure
from app.services.feedback_service import create_feedback_from_azure_response
from app.models.sentence import Sentence


router = APIRouter(
    prefix="/feedback",
    tags=["Feedback"]
)

@router.post("/{user_id}/{sentence_id}")
async def analyze_pronunciation_endpoint(
    user_id: int,
    sentence_id: int,
    audio_file: UploadFile,
    db: Session = Depends(get_db),
):
    sentence = db.query(Sentence).filter(Sentence.sentence_id== sentence_id).first()
    # `Sentence` 테이블의 문장 텍스트 가져오기
    content = sentence.content
    # 1) 오디오 파일 데이터를 bytes로 읽기
    audio_data = await audio_file.read()

    # 2) Azure 발음 평가
    azure_response = await analyze_pronunciation_with_azure(content, audio_data)

    # 3) DB에 피드백 저장
    feedback = await create_feedback_from_azure_response(
        user_id=user_id,
        sentence_id=sentence_id,
        azure_response=azure_response,
        db=db
    )

    # 4) 결과 반환
    return {
        "feedback_id": feedback.feedback_id,
        "accuracy": feedback.accuracy,
        "pronunciation_feedback": feedback.pronunciation_feedback,
    }

@router.post("/analyze", summary="발음 분석", description="Azure Speech SDK를 이용해 발음 평가 결과 반환")
async def analyze_pronunciation_endpoint(
    text: str,
    audio_file: UploadFile,
    db: Session = Depends(get_db),  # 필요 시 사용, 생략 가능
):
    """
    사용자로부터 텍스트와 오디오 파일을 받아 Azure 발음 평가 결과를 반환.
    """
    try:
        # 1. 오디오 데이터를 bytes로 읽기
        audio_data = await audio_file.read()

        # 2. Azure 발음 평가 수행
        result = await analyze_pronunciation_with_azure(text, audio_data)

        # 3. 결과 반환 (Azure 평가 결과 전체 반환)
        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="발음 평가 중 오류가 발생했습니다.")