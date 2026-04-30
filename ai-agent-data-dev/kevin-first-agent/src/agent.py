"""Job Agent 核心"""
import os
from typing import List, Dict, Optional
from langchain_openai import ChatOpenAI
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JobSearchAgent:
    """求职 Agent"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        
        if not self.api_key or self.api_key == "demo-mode-no-key":
            logger.warning("未设置 OPENAI_API_KEY，将使用模拟模式")
            self.llm = None
        else:
            self.llm = ChatOpenAI(
                model="gpt-3.5-turbo",
                api_key=self.api_key,
                base_url=self.base_url,
                temperature=0.2,
            )
    
    def analyze_job(self, job: Dict, user_profile: Optional[Dict] = None):
        if not self.llm:
            return self._mock_analyze(job)
        return self._mock_analyze(job)
    
    def _mock_analyze(self, job: Dict):
        title = job.get("title", "").lower()
        keywords = ["python", "软件", "工程师", "开发", "ai"]
        score = 50
        for kw in keywords:
            if kw in title:
                score += 15
        score = min(score, 100)
        return {
            "match_score": score,
            "is_suitable": score >= 60,
            "reason": f"关键词匹配分数: {score}",
            "suggestions": ["可以考虑投递", "准备技术面试"] if score >= 60 else ["技能匹配度较低"],
        }
    
    def filter_jobs(self, jobs: List[Dict], min_score: int = 60):
        results = []
        for job in jobs:
            analysis = self.analyze_job(job)
            if analysis["match_score"] >= min_score:
                job["analysis"] = analysis
                results.append(job)
        return sorted(results, key=lambda x: x["analysis"]["match_score"], reverse=True)
