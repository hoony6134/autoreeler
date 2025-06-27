# config.py
import os
from typing import Dict, Any

class Config:
    """시스템 전체 설정을 관리하는 클래스"""
    
    # API 키 설정
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    RUNWAY_API_KEY = os.getenv('RUNWAY_API_KEY')
    
    # Instagram Graph API 설정
    INSTAGRAM_ACCESS_TOKEN = os.getenv('INSTAGRAM_ACCESS_TOKEN')
    INSTAGRAM_USER_ID = os.getenv('INSTAGRAM_USER_ID')
    
    # YouTube API 설정
    YOUTUBE_CLIENT_SECRET_FILE = 'client_secret.json'
    YOUTUBE_SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
    
    # 영상 설정
    VIDEO_DURATION = 30  # 초
    VIDEO_RESOLUTION = (1920, 1080)
    AUDIO_SAMPLE_RATE = 44100
    
    # 자막 설정
    SUBTITLE_FONT_SIZE = 24
    SUBTITLE_POSITION = 'bottom'
    
    @classmethod
    def validate_keys(cls) -> bool:
        """필수 API 키들이 설정되었는지 확인"""
        required_keys = [
            cls.GEMINI_API_KEY,
            cls.OPENAI_API_KEY,
            cls.INSTAGRAM_ACCESS_TOKEN,
            cls.INSTAGRAM_USER_ID
        ]
        return all(key is not None for key in required_keys)
