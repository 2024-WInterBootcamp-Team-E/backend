from elevenlabs import voices

# ElevenLabs API Key 설정
API_KEY = "sk_c1b1d94a65f415a2576b8cb59bb952474ea4ebb57d731a37"  # ElevenLabs 대시보드에서 복사한 API Key

# 사용 가능한 음성 목록 가져오기
voices_list = voices(api_key=API_KEY)  # voices() 함수 호출로 음성 목록 가져오기

# Voice 목록 출력
print("Available Voices:")
for voice in voices_list:
    print(f"Voice Name: {voice.name}, Voice ID: {voice.voice_id}")





#API_KEY = "sk_c1b1d94a65f415a2576b8cb59bb952474ea4ebb57d731a37"