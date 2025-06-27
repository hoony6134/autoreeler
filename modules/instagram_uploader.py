# modules/instagram_uploader.py
import requests
import time
from typing import Dict, Any, Optional
import logging
import os

class InstagramUploader:
    """Instagram 업로드를 처리하는 클래스"""
    
    def __init__(self, access_token: str, user_id: str):
        self.access_token = access_token
        self.user_id = user_id
        self.base_url = "https://graph.facebook.com/v18.0"
        self.logger = logging.getLogger(__name__)
    
    def upload_video(self, video_path: str, caption: str, hashtags: List[str] = None) -> Optional[str]:
        """Instagram에 비디오 업로드"""
        try:
            # 1단계: 미디어 컨테이너 생성
            container_id = self._create_media_container(video_path, caption, hashtags)
            
            if not container_id:
                return None
            
            # 2단계: 업로드 완료까지 대기
            if not self._wait_for_upload_completion(container_id):
                return None
            
            # 3단계: 실제 게시
            media_id = self._publish_media(container_id)
            
            if media_id:
                self.logger.info(f"Instagram 업로드 완료: {media_id}")
                return media_id
            
            return None
            
        except Exception as e:
            self.logger.error(f"Instagram 업로드 실패: {str(e)}")
            return None
    
    def _create_media_container(self, video_path: str, caption: str, hashtags: List[str] = None) -> Optional[str]:
        """미디어 컨테이너 생성"""
        try:
            # 비디오 파일을 공개 URL로 업로드 (실제 구현에서는 CDN 사용)
            video_url = self._upload_to_cdn(video_path)
            
            if not video_url:
                return None
            
            # 캡션과 해시태그 결합
            full_caption = caption
            if hashtags:
                full_caption += "\n\n" + " ".join(f"#{tag}" for tag in hashtags)
            
            # Instagram Graph API 호출
            url = f"{self.base_url}/{self.user_id}/media"
            
            data = {
                'video_url': video_url,
                'media_type': 'REELS',
                'caption': full_caption,
                'access_token': self.access_token
            }
            
            response = requests.post(url, data=data)
            response.raise_for_status()
            
            result = response.json()
            container_id = result.get('id')
            
            self.logger.info(f"미디어 컨테이너 생성: {container_id}")
            return container_id
            
        except Exception as e:
            self.logger.error(f"미디어 컨테이너 생성 실패: {str(e)}")
            return None
    
    def _upload_to_cdn(self, video_path: str) -> Optional[str]:
        """비디오를 CDN에 업로드하여 공개 URL 반환"""
        # 실제 구현에서는 AWS S3, Google Cloud Storage 등을 사용
        # 여기서는 임시로 로컬 서버 URL 반환
        try:
            # 로컬 서버에 파일 복사 (실제로는 CDN 업로드)
            filename = os.path.basename(video_path)
            public_url = f"https://your-domain.com/uploads/{filename}"
            
            # 실제 파일 업로드 로직은 여기에 구현
            
            return public_url
            
        except Exception as e:
            self.logger.error(f"CDN 업로드 실패: {str(e)}")
            return None
    
    def _wait_for_upload_completion(self, container_id: str, max_wait: int = 300) -> bool:
        """업로드 완료까지 대기"""
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                url = f"{self.base_url}/{container_id}"
                params = {
                    'fields': 'status_code',
                    'access_token': self.access_token
                }
                
                response = requests.get(url, params=params)
                response.raise_for_status()
                
                result = response.json()
                status = result.get('status_code')
                
                if status == 'FINISHED':
                    self.logger.info("업로드 완료")
                    return True
                elif status == 'ERROR':
                    self.logger.error("업로드 오류 발생")
                    return False
                
                time.sleep(10)  # 10초마다 상태 확인
                
            except Exception as e:
                self.logger.error(f"상태 확인 중 오류: {str(e)}")
                time.sleep(10)
        
        self.logger.warning("업로드 시간 초과")
        return False
    
    def _publish_media(self, container_id: str) -> Optional[str]:
        """미디어 게시"""
        try:
            url = f"{self.base_url}/{self.user_id}/media_publish"
            
            data = {
                'creation_id': container_id,
                'access_token': self.access_token
            }
            
            response = requests.post(url, data=data)
            response.raise_for_status()
            
            result = response.json()
            media_id = result.get('id')
            
            return media_id
            
        except Exception as e:
            self.logger.error(f"미디어 게시 실패: {str(e)}")
            return None
