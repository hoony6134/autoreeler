# modules/youtube_uploader.py
import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from typing import Dict, Any, Optional, List
import logging

class YouTubeUploader:
    """YouTube 업로드를 처리하는 클래스"""
    
    def __init__(self, client_secret_file: str, scopes: List[str]):
        self.client_secret_file = client_secret_file
        self.scopes = scopes
        self.youtube_service = None
        self.logger = logging.getLogger(__name__)
        
        # YouTube API 서비스 초기화
        self._initialize_service()
    
    def _initialize_service(self):
        """YouTube API 서비스 초기화"""
        try:
            creds = None
            token_file = 'token.pickle'
            
            # 저장된 토큰이 있는지 확인
            if os.path.exists(token_file):
                with open(token_file, 'rb') as token:
                    creds = pickle.load(token)
            
            # 유효한 자격 증명이 없는 경우
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.client_secret_file, self.scopes)
                    creds = flow.run_local_server(port=0)
                
                # 토큰 저장
                with open(token_file, 'wb') as token:
                    pickle.dump(creds, token)
            
            # YouTube API 서비스 빌드
            self.youtube_service = build('youtube', 'v3', credentials=creds)
            self.logger.info("YouTube API 서비스 초기화 완료")
            
        except Exception as e:
            self.logger.error(f"YouTube API 초기화 실패: {str(e)}")
    
    def upload_video(self, video_path: str, title: str, description: str, 
                    tags: List[str] = None, category_id: str = "22") -> Optional[str]:
        """YouTube에 비디오 업로드"""
        try:
            if not self.youtube_service:
                self.logger.error("YouTube 서비스가 초기화되지 않았습니다")
                return None
            
            # 비디오 메타데이터 설정
            body = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'tags': tags or [],
                    'categoryId': category_id
                },
                'status': {
                    'privacyStatus': 'public',  # 'private', 'unlisted', 'public'
                    'selfDeclaredMadeForKids': False
                }
            }
            
            # 파일 업로드 설정
            media = MediaFileUpload(
                video_path,
                chunksize=-1,
                resumable=True,
                mimetype='video/mp4'
            )
            
            # 업로드 요청
            insert_request = self.youtube_service.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            # 업로드 실행
            video_id = self._execute_upload(insert_request)
            
            if video_id:
                self.logger.info(f"YouTube 업로드 완료: {video_id}")
                return video_id
            
            return None
            
        except Exception as e:
            self.logger.error(f"YouTube 업로드 실패: {str(e)}")
            return None
    
    def _execute_upload(self, insert_request) -> Optional[str]:
        """업로드 실행 및 진행상황 모니터링"""
        try:
            response = None
            error = None
            retry = 0
            
            while response is None:
                try:
                    status, response = insert_request.next_chunk()
                    
                    if status:
                        progress = int(status.progress() * 100)
                        self.logger.info(f"업로드 진행률: {progress}%")
                        
                except Exception as e:
                    error = e
                    if retry < 3:
                        retry += 1
                        self.logger.warning(f"업로드 재시도 {retry}/3: {str(e)}")
                        time.sleep(2 ** retry)
                    else:
                        raise e
            
            if response is not None:
                if 'id' in response:
                    return response['id']
                else:
                    self.logger.error(f"업로드 실패: {response}")
                    return None
            
        except Exception as e:
            self.logger.error(f"업로드 실행 실패: {str(e)}")
            return None
    
    def set_thumbnail(self, video_id: str, thumbnail_path: str) -> bool:
        """비디오 썸네일 설정"""
        try:
            if not os.path.exists(thumbnail_path):
                self.logger.warning(f"썸네일 파일이 존재하지 않습니다: {thumbnail_path}")
                return False
            
            media = MediaFileUpload(thumbnail_path, mimetype='image/jpeg')
            
            self.youtube_service.thumbnails().set(
                videoId=video_id,
                media_body=media
            ).execute()
            
            self.logger.info(f"썸네일 설정 완료: {video_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"썸네일 설정 실패: {str(e)}")
            return False
    
    def update_video_metadata(self, video_id: str, title: str = None, 
                            description: str = None, tags: List[str] = None) -> bool:
        """비디오 메타데이터 업데이트"""
        try:
            # 현재 비디오 정보 가져오기
            video_response = self.youtube_service.videos().list(
                part='snippet',
                id=video_id
            ).execute()
            
            if not video_response['items']:
                self.logger.error(f"비디오를 찾을 수 없습니다: {video_id}")
                return False
            
            snippet = video_response['items'][0]['snippet']
            
            # 업데이트할 정보 설정
            if title:
                snippet['title'] = title
            if description:
                snippet['description'] = description
            if tags:
                snippet['tags'] = tags
            
            # 업데이트 요청
            self.youtube_service.videos().update(
                part='snippet',
                body={
                    'id': video_id,
                    'snippet': snippet
                }
            ).execute()
            
            self.logger.info(f"메타데이터 업데이트 완료: {video_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"메타데이터 업데이트 실패: {str(e)}")
            return False
