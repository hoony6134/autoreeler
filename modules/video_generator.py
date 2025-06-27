# modules/video_generator.py
import requests
import time
import json
from typing import Dict, Any, Optional, List
import logging
from moviepy.editor import VideoFileClip, concatenate_videoclips, TextClip, CompositeVideoClip
import tempfile
import os

class VideoGenerator:
    """AI 영상 생성을 처리하는 클래스"""
    
    def __init__(self, runway_api_key: str = None, veo_api_key: str = None):
        self.runway_api_key = runway_api_key
        self.veo_api_key = veo_api_key
        self.logger = logging.getLogger(__name__)
    
    def generate_video_from_script(self, script_ Dict[str, Any], product_images: List[str]) -> Optional[str]:
        """스크립트 데이터를 바탕으로 영상 생성"""
        try:
            video_clips = []
            
            # 장면별 영상 생성
            for i, scene in enumerate(script_data.get('video_scenes', [])):
                scene_prompt = self._create_scene_prompt(scene, script_data)
                
                # 상품 이미지가 있는 경우 이미지-투-비디오로 생성
                if i < len(product_images):
                    video_path = self._generate_video_from_image(
                        scene_prompt, 
                        product_images[i], 
                        scene['duration']
                    )
                else:
                    # 텍스트-투-비디오로 생성
                    video_path = self._generate_video_from_text(
                        scene_prompt, 
                        scene['duration']
                    )
                
                if video_path:
                    clip = VideoFileClip(video_path)
                    video_clips.append(clip)
            
            # 영상 클립들을 하나로 합치기
            if video_clips:
                final_video = concatenate_videoclips(video_clips)
                output_path = f"output/videos/final_video_{int(time.time())}.mp4"
                final_video.write_videofile(output_path, fps=24)
                
                # 메모리 정리
                for clip in video_clips:
                    clip.close()
                final_video.close()
                
                self.logger.info(f"영상 생성 완료: {output_path}")
                return output_path
            
            return None
            
        except Exception as e:
            self.logger.error(f"영상 생성 실패: {str(e)}")
            return None
    
    def _create_scene_prompt(self, scene: Dict[str, Any], script_ Dict[str, Any]) -> str:
        """장면별 프롬프트 생성"""
        base_prompt = scene.get('description', '')
        
        # 상품 관련 키워드 추가
        product_context = f"product showcase, commercial video, {script_data.get('title', '')}"
        
        return f"{base_prompt}, {product_context}, high quality, professional lighting, 4K resolution"
    
    def _generate_video_from_image(self, prompt: str, image_url: str, duration: int) -> Optional[str]:
        """이미지를 기반으로 영상 생성 (Runway API 사용)"""
        try:
            if not self.runway_api_key:
                self.logger.warning("Runway API 키가 없습니다. 기본 영상을 생성합니다.")
                return self._create_default_video(duration)
            
            # Runway API 호출
            headers = {
                'Authorization': f'Bearer {self.runway_api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'prompt': prompt,
                'image_url': image_url,
                'duration': duration,
                'aspect_ratio': '16:9'
            }
            
            # 영상 생성 요청
            response = requests.post(
                'https://api.runwayml.com/v1/generate/video',
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                task_id = result.get('task_id')
                
                # 생성 완료까지 대기
                video_url = self._wait_for_video_completion(task_id)
                if video_url:
                    return self._download_video(video_url)
            
            return self._create_default_video(duration)
            
        except Exception as e:
            self.logger.error(f"이미지 기반 영상 생성 실패: {str(e)}")
            return self._create_default_video(duration)
    
    def _generate_video_from_text(self, prompt: str, duration: int) -> Optional[str]:
        """텍스트 프롬프트로 영상 생성 (Veo API 또는 대체 방법)"""
        try:
            # Google Veo API 사용 시도
            if self.veo_api_key:
                return self._generate_with_veo(prompt, duration)
            
            # 대체 방법: 정적 이미지로 영상 생성
            return self._create_default_video(duration)
            
        except Exception as e:
            self.logger.error(f"텍스트 기반 영상 생성 실패: {str(e)}")
            return self._create_default_video(duration)
    
    def _generate_with_veo(self, prompt: str, duration: int) -> Optional[str]:
        """Google Veo API를 사용한 영상 생성"""
        try:
            # Veo API 구현 (실제 API 엔드포인트가 공개되면 업데이트)
            headers = {
                'Authorization': f'Bearer {self.veo_api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'prompt': prompt,
                'duration_seconds': duration,
                'aspect_ratio': '16:9'
            }
            
            # API 호출 로직
            # response = requests.post('veo_api_endpoint', headers=headers, json=data)
            
            # 현재는 기본 영상 반환
            return self._create_default_video(duration)
            
        except Exception as e:
            self.logger.error(f"Veo API 호출 실패: {str(e)}")
            return self._create_default_video(duration)
    
    def _create_default_video(self, duration: int) -> str:
        """기본 영상 생성 (텍스트 오버레이 포함)"""
        try:
            # 단색 배경으로 영상 생성
            txt_clip = TextClip(
                "쿠팡 상품 소개",
                fontsize=50,
                color='white',
                bg_color='blue',
                size=(1920, 1080)
            ).set_duration(duration)
            
            output_path = f"output/videos/default_scene_{int(time.time())}.mp4"
            txt_clip.write_videofile(output_path, fps=24)
            txt_clip.close()
            
            return output_path
            
        except Exception as e:
            self.logger.error(f"기본 영상 생성 실패: {str(e)}")
            return None
    
    def _wait_for_video_completion(self, task_id: str, max_wait: int = 300) -> Optional[str]:
        """영상 생성 완료까지 대기"""
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                headers = {'Authorization': f'Bearer {self.runway_api_key}'}
                response = requests.get(
                    f'https://api.runwayml.com/v1/tasks/{task_id}',
                    headers=headers
                )
                
                if response.status_code == 200:
                    result = response.json()
                    status = result.get('status')
                    
                    if status == 'completed':
                        return result.get('video_url')
                    elif status == 'failed':
                        self.logger.error(f"영상 생성 실패: {result.get('error')}")
                        return None
                
                time.sleep(10)  # 10초마다 상태 확인
                
            except Exception as e:
                self.logger.error(f"상태 확인 중 오류: {str(e)}")
                time.sleep(10)
        
        self.logger.warning("영상 생성 시간 초과")
        return None
    
    def _download_video(self, video_url: str) -> str:
        """생성된 영상 다운로드"""
        try:
            response = requests.get(video_url, stream=True)
            response.raise_for_status()
            
            output_path = f"output/videos/downloaded_{int(time.time())}.mp4"
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return output_path
            
        except Exception as e:
            self.logger.error(f"영상 다운로드 실패: {str(e)}")
            return None
