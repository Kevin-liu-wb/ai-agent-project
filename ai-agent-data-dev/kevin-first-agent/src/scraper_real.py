"""猎聘网真实抓取器 - 使用 Selenium"""
import time
import random
import logging
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LiepinScraperReal:
    """猎聘网真实抓取器"""
    
    def __init__(self, headless: bool = True):
        self.base_url = "https://c.liepin.com"
        self.driver = None
        self.headless = headless
        self._init_driver()
    
    def _init_driver(self):
        """初始化浏览器驱动"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # 设置 User-Agent
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # 禁用自动化特征
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                    Object.defineProperty(navigator, "webdriver", {
                        get: () => undefined
                    })
                """
            })
            logger.info("浏览器驱动初始化成功")
        except Exception as e:
            logger.error(f"浏览器驱动初始化失败: {e}")
            self.driver = None
    
    def search_jobs(
        self,
        keyword: str = "软件工程师",
        location: str = "上海浦东",
        pages: int = 1
    ) -> List[Dict]:
        """
        搜索猎聘网职位
        
        Args:
            keyword: 搜索关键词
            location: 工作地点
            pages: 抓取页数
        """
        if not self.driver:
            logger.error("浏览器驱动未初始化")
            return []
        
        jobs = []
        
        try:
            # 构建搜索 URL
            # 猎聘网搜索 URL 格式
            search_url = f"{self.base_url}/so/?keywords={keyword}"
            if location:
                search_url += f"&dqs=070020"  # 上海浦东的地区代码可能需要调整
            
            logger.info(f"访问: {search_url}")
            self.driver.get(search_url)
            
            # 等待页面加载
            time.sleep(3)
            
            # 获取职位列表
            for page in range(pages):
                logger.info(f"正在抓取第 {page + 1} 页...")
                
                # 滚动页面加载更多
                self._scroll_page()
                
                # 解析职位列表
                page_jobs = self._parse_job_list()
                jobs.extend(page_jobs)
                
                logger.info(f"第 {page + 1} 页找到 {len(page_jobs)} 个职位")
                
                # 随机延迟，避免请求过快
                if page < pages - 1:
                    delay = random.uniform(2, 4)
                    logger.info(f"等待 {delay:.1f} 秒...")
                    time.sleep(delay)
                
                # 点击下一页
                if not self._click_next_page():
                    break
        
        except Exception as e:
            logger.error(f"抓取失败: {e}")
        
        finally:
            # 关闭浏览器
            self.close()
        
        return jobs
    
    def _scroll_page(self):
        """滚动页面加载更多内容"""
        try:
            for _ in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
        except Exception as e:
            logger.warning(f"滚动页面失败: {e}")
    
    def _parse_job_list(self) -> List[Dict]:
        """解析职位列表"""
        jobs = []
        
        try:
            # 获取页面源码
            soup = BeautifulSoup(self.driver.page_source, "lxml")
            
            # 猎聘网职位卡片选择器（需要根据实际页面调整）
            job_cards = soup.find_all("div", class_="job-card-pc")
            
            if not job_cards:
                # 备选选择器
                job_cards = soup.find_all("div", class_="job-item")
            
            if not job_cards:
                # 再试一次
                job_cards = soup.select("[data-selector=\"job-card\"]")
            
            for card in job_cards:
                try:
                    job = self._extract_job_info(card)
                    if job:
                        jobs.append(job)
                except Exception as e:
                    logger.warning(f"解析职位卡片失败: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"解析职位列表失败: {e}")
        
        return jobs
    
    def _extract_job_info(self, card) -> Optional[Dict]:
        """提取单个职位信息"""
        try:
            # 尝试多个可能的选择器
            title_elem = (card.find("a", class_="job-title") or 
                       card.find("h3") or 
                       card.find("a", attrs={"data-selector": "job-title"}))
            
            company_elem = (card.find("a", class_="company-name") or 
                          card.find("div", class_="company") or
                          card.find("span", class_="company"))
            
            salary_elem = (card.find("span", class_="salary") or 
                          card.find("div", class_="salary"))
            
            if not title_elem:
                return None
            
            title = title_elem.get_text(strip=True)
            company = company_elem.get_text(strip=True) if company_elem else "未知公司"
            salary_text = salary_elem.get_text(strip=True) if salary_elem else "薪资面议"
            
            # 提取薪资范围
            salary_min, salary_max = self._parse_salary(salary_text)
            
            # 生成唯一ID
            job_id = f"liepin_{hash(title + company) % 10000000}"
            
            return {
                "job_id": job_id,
                "title": title,
                "company": company,
                "location": "上海浦东",
                "salary_text": salary_text,
                "salary_min": salary_min,
                "salary_max": salary_max,
                "experience": "3-5年",  # 默认，实际需要从详情页获取
                "education": "本科",
                "description": "",  # 需要从详情页获取
                "requirements": "",  # 需要从详情页获取
                "tags": [],
                "source": "liepin",
                "url": title_elem.get("href", "") if title_elem.has_attr("href") else "",
            }
        
        except Exception as e:
            logger.warning(f"提取职位信息失败: {e}")
            return None
    
    def _parse_salary(self, salary_text: str):
        """解析薪资文本"""
        import re
        
        salary_min = None
        salary_max = None
        
        # 匹配 "25K-40K" 或 "25-40K" 或 "25万-40万"
        match = re.search(r"(\d+)[Kk万]?[-~](\d+)[Kk万]?", salary_text)
        if match:
            salary_min = int(match.group(1))
            salary_max = int(match.group(2))
        
        return salary_min, salary_max
    
    def _click_next_page(self) -> bool:
        """点击下一页"""
        try:
            # 尝试找到下一页按钮
            next_btn = self.driver.find_element(By.CSS_SELECTOR, ".next-page, .pagination-next, [data-selector=\"next-page\"]")
            
            if "disabled" in next_btn.get_attribute("class"):
                return False
            
            next_btn.click()
            time.sleep(2)
            return True
        
        except Exception as e:
            logger.warning(f"点击下一页失败: {e}")
            return False
    
    def get_job_detail(self, url: str) -> Optional[Dict]:
        """获取职位详情"""
        if not self.driver:
            return None
        
        try:
            self.driver.get(url)
            time.sleep(2)
            
            soup = BeautifulSoup(self.driver.page_source, "lxml")
            
            description = soup.find("div", class_="job-description")
            requirements = soup.find("div", class_="job-require")
            
            return {
                "description": description.get_text(strip=True) if description else "",
                "requirements": requirements.get_text(strip=True) if requirements else "",
            }
        
        except Exception as e:
            logger.error(f"获取职位详情失败: {e}")
            return None
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("浏览器已关闭")
            except Exception as e:
                logger.warning(f"关闭浏览器失败: {e}")


# 为了向后兼容，提供别名
LiepinScraper = LiepinScraperReal
