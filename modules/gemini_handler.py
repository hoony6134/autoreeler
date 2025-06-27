# modules/gemini_handler.py
import google.generativeai as genai
from typing import Dict, Any, Optional
import json
import logging

class GeminiHandler:
    """Google Gemini API를 처리하는 클래스"""
    
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.logger = logging.getLogger(__name__)
    
    def generate_video_script(self, product_info: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """상품 정보를 바탕으로 영상 스크립트 생성"""
        try:
            prompt = self._create_script_prompt(product_info)
            
            response = self.model.generate_content(prompt)
            script_data = self._parse_script_response(response.text)
            
            self.logger.info("영상 스크립트 생성 완료")
            return script_data
            
        except Exception as e:
            self.logger.error(f"스크립트 생성 실패: {str(e)}")
            return None
    
    def _create_script_prompt(self, product_info: Dict[str, Any]) -> str:
        """스크립트 생성을 위한 프롬프트 작성"""
        return f"""
다음 쿠팡 상품 정보를 바탕으로 30초 분량의 흥미로운 상품 소개 영상 스크립트를 작성해주세요:

상품명: {product_info['title']}
가격: {product_info['price']}원
별점: {product_info['rating']}/5.0
리뷰 수: {product_info['review_count']}개
상품 설명: {product_info['description']}

다음 JSON 형식으로 응답해주세요:
{{
    "title": "영상 제목 (흥미롭고 클릭을 유도하는)",
    "description": "영상 설명 (SEO 최적화된)",
    "script": "30초 분량의 자연스러운 한국어 내레이션 스크립트",
    "hashtags": ["해시태그1", "해시태그2", "해시태그3", "해시태그4", "해시태그5"],
    "video_scenes": [
        {{
            "scene": 1,
            "description": "첫 번째 장면 설명",
            "duration": 5
        }},
        {{
            "scene": 2,
            "description": "두 번째 장면 설명",
            "duration": 10
        }},
        {{
            "scene": 3,
            "description": "세 번째 장면 설명",
            "duration": 15
        }}
    ]
}}

스크립트는 다음 요소를 포함해야 합니다:
1. 흥미로운 오프닝 (3초)
2. 상품의 핵심 특징 소개 (15초)
3. 가격과 혜택 강조 (7초)
4. 행동 유도 멘트 (5초)

자연스럽고 친근한 톤으로 작성하며, 시청자의 관심을 끌 수 있도록 해주세요.
"""
    
    def _parse_script_response(self, response_text: str) -> Dict[str, Any]:
        """Gemini 응답을 파싱하여 구조화된 데이터로 변환"""
        try:
            # JSON 부분만 추출
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_text = response_text[start_idx:end_idx]
                return json.loads(json_text)
            else:
                # JSON 형식이 아닌 경우 기본 구조로 파싱
                return self._fallback_parse(response_text)
                
        except json.JSONDecodeError:
            return self._fallback_parse(response_text)
    
    def _fallback_parse(self, text: str) -> Dict[str, Any]:
        """JSON 파싱 실패 시 대체 파싱 방법"""
        return {
            "title": "쿠팡 상품 소개",
            "description": "AI가 생성한 상품 소개 영상입니다.",
            "script": text[:500],  # 첫 500자를 스크립트로 사용
            "hashtags": ["쿠팡", "상품추천", "쇼핑", "AI"],
            "video_scenes": [
                {"scene": 1, "description": "상품 소개", "duration": 30}
            ]
        }
    
    def generate_image_prompts(self, script_ Dict[str, Any]) -> list:
        """영상 장면별 이미지 생성 프롬프트 생성"""
        try:
            prompt = f"""
다음 영상 스크립트와 장면 정보를 바탕으로, 각 장면에 적합한 이미지 생성 프롬프트를 영어로 작성해주세요:

스크립트: {script_data.get('script', '')}
장면 정보: {json.dumps(script_data.get('video_scenes', []), ensure_ascii=False)}

각 장면마다 다음 형식으로 응답해주세요:
- 상품의 특징을 잘 보여주는 시각적 요소
- 깔끔하고 전문적인 스타일
- 고화질, 상업적 용도에 적합한 이미지

JSON 배열 형식으로 응답:
["scene 1 prompt", "scene 2 prompt", "scene 3 prompt"]
"""
            
            response = self.model.generate_content(prompt)
            prompts = self._parse_prompts_response(response.text)
            
            self.logger.info(f"이미지 프롬프트 {len(prompts)}개 생성 완료")
            return prompts
            
        except Exception as e:
            self.logger.error(f"이미지 프롬프트 생성 실패: {str(e)}")
            return ["product showcase, professional lighting, high quality"]
    
    def _parse_prompts_response(self, response_text: str) -> list:
        """프롬프트 응답 파싱"""
        try:
            start_idx = response_text.find('[')
            end_idx = response_text.rfind(']') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_text = response_text[start_idx:end_idx]
                return json.loads(json_text)
            else:
                # 기본 프롬프트 반환
                return ["professional product photography, high quality, commercial use"]
                
        except json.JSONDecodeError:
            return ["professional product photography, high quality, commercial use"]
