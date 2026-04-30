"""职位网站抓取器"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import time
import random
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LiepinScraper:
    """猎聘网抓取器"""
    
    def __init__(self):
        self.base_url = "https://www.liepin.com"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        })
    
    def search_jobs(
        self,
        keyword: str = "软件工程师",
        location: str = "上海浦东",
        page: int = 1
    ) -> List[Dict]:
        """
        搜索职位
        
        注意：实际使用时可能需要处理反爬虫、登录等问题
        本示例提供基础结构，可根据实际情况调整
        """
        jobs = []
        
        try:
            # 猎聘搜索 URL（可能需要根据实际页面调整）
            search_url = f"{self.base_url}/zhaopin/"
            params = {
                "key": keyword,
                "dq": location,
                "currentPage": page,
            }
            
            logger.info(f"正在搜索: {keyword} @ {location}, 第{page}页")
            
            response = self.session.get(search_url, params=params, timeout=30)
            response.raise_for_status()
            
            # 解析页面
            soup = BeautifulSoup(response.text, "lxml")
            job_cards = soup.find_all("div", class_="job-card-pc")
            
            for card in job_cards:
                try:
                    job = self._parse_job_card(card)
                    if job:
                        jobs.append(job)
                except Exception as e:
                    logger.warning(f"解析职位卡片失败: {e}")
                    continue
            
            # 随机延迟，避免请求过快
            time.sleep(random.uniform(1, 3))
            
        except Exception as e:
            logger.error(f"抓取失败: {e}")
        
        return jobs
    
    def _parse_job_card(self, card) -> Optional[Dict]:
        """解析单个职位卡片"""
        try:
            title_elem = card.find("a", class_="job-title")
            company_elem = card.find("a", class_="company-name")
            salary_elem = card.find("span", class_="salary")
            
            if not title_elem:
                return None
            
            return {
                "title": title_elem.get_text(strip=True),
                "company": company_elem.get_text(strip=True) if company_elem else "未知公司",
                "salary_text": salary_elem.get_text(strip=True) if salary_elem else "薪资面议",
                "location": "上海浦东",  # 从搜索条件获取
                "url": title_elem.get("href", ""),
                "source": "liepin",
                "job_id": self._extract_job_id(title_elem.get("href", "")),
            }
        except Exception as e:
            logger.warning(f"解析职位详情失败: {e}")
            return None
    
    def _extract_job_id(self, url: str) -> str:
        """从 URL 提取职位 ID"""
        import re
        match = re.search(r"/(\d+)\.shtml", url)
        return match.group(1) if match else url.split("/")[-1]
    
    def get_job_detail(self, url: str) -> Optional[Dict]:
        """获取职位详情"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "lxml")
            
            # 提取详情（根据实际页面结构调整选择器）
            description = soup.find("div", class_="job-description")
            requirements = soup.find("div", class_="job-requirements")
            
            return {
                "description": description.get_text(strip=True) if description else "",
                "requirements": requirements.get_text(strip=True) if requirements else "",
            }
        except Exception as e:
            logger.error(f"获取职位详情失败: {e}")
            return None


class MockScraper:
    """模拟抓取器（用于测试）"""
    
    def search_jobs(self, keyword: str = "软件工程师", location: str = "上海浦东", **kwargs):
        """返回模拟数据"""
        return [
            {
                "title": f"{keyword} - Python方向",
                "company": f"示例科技公司 {i}",
                "salary_text": "25K-40K",
                "salary_min": 25,
                "salary_max": 40,
                "location": location,
                "experience": "3-5年",
                "education": "本科",
                "tags": ["Python", "AI", "后端"],
                "source": "mock",
                "job_id": f"mock_{i}",
                "url": f"https://example.com/job/{i}",
                "description": "负责AI Agent系统开发...",
                "requirements": "熟悉Python, LangChain...",
            }
            for i in range(1, 6)
        ]
