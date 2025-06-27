# modules/audio_generator.py
from openai import OpenAI
import io
import wave
from typing import Optional
import logging
import os

class AudioGenerator:
    """AI 음성 생성을 처리하는 클래스"""
    
    def __init__(self, openai_api_key: str):
        self.client = OpenAI(api_key=openai_api_key)
        self.logger = logging.getLogger(__name__)
    
    def generate_speech(self, script: str, voice: str = "alloy") -> Optional[str]:
        """텍스트를 음성으로 변환"""
        try:
            # OpenAI TTS API 호출
            response = self.client.audio.speech.create(
                model="tts-1-hd",
                voice=voice,
                input=script,
                response_format="mp3"
            )
            
            # 오디오 파일 저장
            output_path = f"output/audio/speech_{int(time.time())}.mp3"
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            self.logger.info(f"음성 생성 완료: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"음성 생성 실패: {str(e)}")
            return None
    
    def get_audio_duration(self, audio_path: str) -> float:
        """오디오 파일의 재생 시간 반환"""
        try:
            from moviepy.editor import AudioFileClip
            audio = AudioFileClip(audio_path)
            duration = audio.duration
            audio.close()
            return duration
            
        except Exception as e:
            self.logger.error(f"오디오 길이 측정 실패: {str(e)}")
            return 0.0
    
    def adjust_speech_speed(self, audio_path: str, target_duration: float) -> Optional[str]:
        """음성 속도를 조정하여 타겟 시간에 맞춤"""
        try:
            from moviepy.editor import AudioFileClip
            
            audio = AudioFileClip(audio_path)
            current_duration = audio.duration
            
            if current_duration > 0:
                speed_factor = current_duration / target_duration
                
                # 속도 조정 (0.5x ~ 2.0x 범위 내에서)
                speed_factor = max(0.5, min(2.0, speed_factor))
                
                # 새로운 오디오 생성
                adjusted_audio = audio.fx.speedx(speed_factor)
                
                output_path = f"output/audio/adjusted_{int(time.time())}.mp3"
                adjusted_audio.write_audiofile(output_path, verbose=False, logger=None)
                
                audio.close()
                adjusted_audio.close()
                
                self.logger.info(f"음성 속도 조정 완료: {output_path}")
                return output_path
            
            return audio_path
            
        except Exception as e:
            self.logger.error(f"음성 속도 조정 실패: {str(e)}")
            return audio_path
