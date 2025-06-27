# modules/coupang_scraper.py
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import re
import json
from typing import Dict, Optional
import logging

class CoupangScraper:
    """쿠팡 상품 정보를 추출하는 클래스"""
    
    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)
    
    def get_headers(self) -> Dict[str, str]:
        """랜덤 User-Agent 헤더 생성"""
        return {
            'User-Agent': self.ua.random,
            'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
    
    def extract_product_info(self, coupang_url: str) -> Optional[Dict[str, Any]]:
        """쿠팡 URL에서 상품 정보를 추출"""
        try:
            # URL 유효성 검사
            if not self._is_valid_coupang_url(coupang_url):
                raise ValueError("유효하지 않은 쿠팡 URL입니다")
            
            # 페이지 요청
            response = self.session.get(coupang_url, headers=self.get_headers())
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 상품 정보 추출
            product_info = {
                'title': self._extract_title(soup),
                'price': self._extract_price(soup),
                'original_price': self._extract_original_price(soup),
                'rating': self._extract_rating(soup),
                'review_count': self._extract_review_count(soup),
                'description': self._extract_description(soup),
                'images': self._extract_images(soup),
                'url': coupang_url
            }
            
            self.logger.info(f"상품 정보 추출 완료: {product_info['title']}")
            return product_info
            
        except Exception as e:
            self.logger.error(f"상품 정보 추출 실패: {str(e)}")
            return None
    
    def _is_valid_coupang_url(self, url: str) -> bool:
        """쿠팡 URL 유효성 검사"""
        coupang_patterns = [
            r'https?://.*coupang\.com/vp/products/\d+',
            r'https?://.*coupang\.com/np/search'
        ]
        return any(re.match(pattern, url) for pattern in coupang_patterns)
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """상품명 추출"""
        selectors = [
            'h1.prod-buy-header__title',
            '.prod-title',
            'h1[class*="title"]'
        ]
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        return "상품명 없음"
    
    def _extract_price(self, soup: BeautifulSoup) -> str:
        """판매가 추출"""
        selectors = [
            '.total-price strong',
            '.price-value',
            '[class*="price"] strong'
        ]
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                price_text = element.get_text(strip=True)
                return re.sub(r'[^\d,]', '', price_text)
        return "가격 정보 없음"
    
    def _extract_original_price(self, soup: BeautifulSoup) -> str:
        """정가 추출"""
        selectors = [
            '.origin-price',
            '.base-price',
            '[class*="original-price"]'
        ]
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return re.sub(r'[^\d,]', '', element.get_text(strip=True))
        return ""
    
    def _extract_rating(self, soup: BeautifulSoup) -> str:
        """별점 추출"""
        selectors = [
            '.rating-star-num',
            '.prod-rating-score',
            '[class*="rating"] span'
        ]
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        return "0"
    
    def _extract_review_count(self, soup: BeautifulSoup) -> str:
        """리뷰 수 추출"""
        selectors = [
            '.rating-total-count',
            '.prod-rating-count',
            '[class*="review-count"]'
        ]
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                count_text = element.get_text(strip=True)
                return re.sub(r'[^\d]', '', count_text)
        return "0"
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """상품 설명 추출"""
        selectors = [
            '.prod-description',
            '.product-detail',
            '[class*="description"]'
        ]
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)[:500]  # 최대 500자
        return "상품 설명 없음"
    
    def _extract_images(self, soup: BeautifulSoup) -> list:
        """상품 이미지 URL 추출"""
        images = []
        img_selectors = [
            '.prod-image__detail img',
            '.product-image img',
            '[class*="image"] img'
        ]
        
        for selector in img_selectors:
            img_elements = soup.select(selector)
            for img in img_elements[:5]:  # 최대 5개 이미지
                src = img.get('src') or img.get('data-src')
                if src and src.startswith('http'):
                    images.append(src)
        
        return list(set(images))  # 중복 제거
