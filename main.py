# main.py
import logging
import sys
import time
from modules.coupang_scraper import CoupangScraper
from modules.gemini_handler import GeminiHandler
from modules.video_generator import VideoGenerator
from modules.audio_generator import AudioGenerator
from modules.subtitle_generator import SubtitleGenerator
from modules.instagram_uploader import InstagramUploader
from modules.youtube_uploader import YouTubeUploader
from config import Config

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/automation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class CoupangVideoAutomation:
    """쿠팡 영상 자동화 메인 클래스"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # API 키 검증
        if not Config.validate_keys():
            raise ValueError("필수 API 키가 설정되지 않았습니다")
        
        # 모듈 초기화
        self.scraper = CoupangScraper()
        self.gemini = GeminiHandler(Config.GEMINI_API_KEY)
        self.video_gen = VideoGenerator(Config.RUNWAY_API_KEY)
        self.audio_gen = AudioGenerator(Config.OPENAI_API_KEY)
        self.subtitle_gen = SubtitleGenerator()
        self.instagram = InstagramUploader(
            Config.INSTAGRAM_ACCESS_TOKEN, 
            Config.INSTAGRAM_USER_ID
        )
        self.youtube = YouTubeUploader(
            Config.YOUTUBE_CLIENT_SECRET_FILE,
            Config.YOUTUBE_SCOPES
        )
    
    def process_coupang_link(self, coupang_url: str) -> Dict[str, Any]:
        """쿠팡 링크를 처리하여 영상 생성 및 업로드"""
        try:
            self.logger.info(f"쿠팡 링크 처리 시작: {coupang_url}")
            
            # 1. 쿠팡 상품 정보 추출
            self.logger.info("1. 상품 정보 추출 중...")
            product_info = self.scraper.extract_product_info(coupang_url)
            
            if not product_info:
                raise Exception("상품 정보 추출 실패")
            
            # 2. Gemini로 영상 스크립트 생성
            self.logger.info("2. 영상 스크립트 생성 중...")
            script_data = self.gemini.generate_video_script(product_info)
            
            if not script_
                raise Exception("스크립트 생성 실패")
            
            # 3. AI 음성 생성
            self.logger.info("3. AI 음성 생성 중...")
            audio_path = self.audio_gen.generate_speech(
                script_data['script'],
                voice="alloy"
            )
            
            if not audio_path:
                raise Exception("음성 생성 실패")
            
            # 4. 자막 생성
            self.logger.info("4. 자막 생성 중...")
            subtitle_path = self.subtitle_gen.generate_subtitles_from_script(
                script_data['script'],
                self.audio_gen.get_audio_duration(audio_path)
            )
            
            # 5. AI 영상 생성
            self.logger.info("5. AI 영상 생성 중...")
            video_path = self.video_gen.generate_video_from_script(
                script_data,
                product_info.get('images', [])
            )
            
            if not video_path:
                raise Exception("영상 생성 실패")
            
            # 6. 영상에 음성과 자막 합성
            self.logger.info("6. 영상 합성 중...")
            final_video_path = self._compose_final_video(
                video_path, audio_path, subtitle_path
            )
            
            if not final_video_path:
                raise Exception("영상 합성 실패")
            
            # 7. 소셜미디어 업로드
            self.logger.info("7. 소셜미디어 업로드 중...")
            upload_results = self._upload_to_social_media(
                final_video_path, script_data
            )
            
            # 결과 반환
            result = {
                'success': True,
                'product_info': product_info,
                'script_data': script_data,
                'video_path': final_video_path,
                'upload_results': upload_results,
                'processing_time': time.time()
            }
            
            self.logger.info("모든 처리 완료!")
            return result
            
        except Exception as e:
            self.logger.error(f"처리 중 오류 발생: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'processing_time': time.time()
            }
    
    def _compose_final_video(self, video_path: str, audio_path: str, 
                           subtitle_path: str = None) -> Optional[str]:
        """영상, 음성, 자막을 합성하여 최종 영상 생성"""
        try:
            from moviepy.editor import VideoFileClip, CompositeAudioClip
            
            # 비디오 로드
            video = VideoFileClip(video_path)
            
            # 오디오 로드 및 합성
            if audio_path:
                from moviepy.editor import AudioFileClip
                audio = AudioFileClip(audio_path)
                
                # 비디오 길이에 맞춰 오디오 조정
                if audio.duration != video.duration:
                    if audio.duration > video.duration:
                        audio = audio.subclip(0, video.duration)
                    else:
                        # 오디오가 짧은 경우 비디오 길이 조정
                        video = video.subclip(0, audio.duration)
                
                video = video.set_audio(audio)
            
            # 자막 추가
            if subtitle_path and os.path.exists(subtitle_path):
                video = self.subtitle_gen.add_subtitles_to_video(
                    video, subtitle_path
                )
            
            # 최종 영상 저장
            output_path = f"output/videos/final_{int(time.time())}.mp4"
            video.write_videofile(
                output_path,
                fps=24,
                codec='libx264',
                audio_codec='aac'
            )
            
            # 메모리 정리
            video.close()
            if 'audio' in locals():
                audio.close()
            
            return output_path
            
        except Exception as e:
            self.logger.error(f"영상 합성 실패: {str(e)}")
            return None
    
    def _upload_to_social_media(self, video_path: str, 
                              script_ Dict[str, Any]) -> Dict[str, Any]:
        """소셜미디어에 영상 업로드"""
        results = {}
        
        try:
            # Instagram 업로드
            self.logger.info("Instagram 업로드 중...")
            instagram_id = self.instagram.upload_video(
                video_path,
                script_data['description'],
                script_data.get('hashtags', [])
            )
            results['instagram'] = {
                'success': instagram_id is not None,
                'media_id': instagram_id
            }
            
            # YouTube 업로드
            self.logger.info("YouTube 업로드 중...")
            youtube_id = self.youtube.upload_video(
                video_path,
                script_data['title'],
                script_data['description'],
                script_data.get('hashtags', [])
            )
            results['youtube'] = {
                'success': youtube_id is not None,
                'video_id': youtube_id
            }
            
        except Exception as e:
            self.logger.error(f"소셜미디어 업로드 중 오류: {str(e)}")
            results['error'] = str(e)
        
        return results

def main():
    """메인 실행 함수"""
    try:
        # 자동화 시스템 초기화
        automation = CoupangVideoAutomation()
        
        # 사용자 입력 받기
        coupang_url = input("쿠팡 상품 URL을 입력하세요: ").strip()
        
        if not coupang_url:
            print("URL이 입력되지 않았습니다.")
            return
        
        # 처리 시작
        print("처리를 시작합니다...")
        result = automation.process_coupang_link(coupang_url)
        
        # 결과 출력
        if result['success']:
            print("\n✅ 처리 완료!")
            print(f"📱 Instagram: {'성공' if result['upload_results'].get('instagram', {}).get('success') else '실패'}")
            print(f"🎥 YouTube: {'성공' if result['upload_results'].get('youtube', {}).get('success') else '실패'}")
            print(f"🎬 생성된 영상: {result['video_path']}")
        else:
            print(f"\n❌ 처리 실패: {result['error']}")
    
    except KeyboardInterrupt:
        print("\n처리가 중단되었습니다.")
    except Exception as e:
        print(f"\n오류 발생: {str(e)}")

if __name__ == "__main__":
    main()
