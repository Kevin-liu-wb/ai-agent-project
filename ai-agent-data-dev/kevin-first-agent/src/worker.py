"""任务处理器 - 使用 Celery + Redis"""
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from celery import Celery
from sqlalchemy.orm import Session
from typing import Dict
import logging

from config.database import SessionLocal, init_db
from config.redis_client import redis_client
from src.models import Job, SearchHistory
from src.scraper import MockScraper, LiepinScraper
from src.agent import JobSearchAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Celery 配置
celery_app = Celery(
    "job_agent",
    broker=f"redis://{os.getenv(REDIS_HOST, ai-agent-redis)}:{os.getenv(REDIS_PORT, 6379)}/0",
    backend=f"redis://{os.getenv(REDIS_HOST, ai-agent-redis)}:{os.getenv(REDIS_PORT, 6379)}/1",
)


@celery_app.task
def search_jobs_task(keyword: str, location: str, search_id: int):
    """搜索任务"""
    logger.info(f"开始搜索: {keyword} @ {location}")
    
    db = SessionLocal()
    scraper = MockScraper()  # 使用模拟抓取器，可切换为 LiepinScraper()
    
    try:
        # 执行搜索
        jobs = scraper.search_jobs(keyword=keyword, location=location)
        
        # 保存到数据库
        for job_data in jobs:
            existing = db.query(Job).filter(Job.job_id == job_data["job_id"]).first()
            if not existing:
                job = Job(**job_data)
                db.add(job)
        
        db.commit()
        
        # 更新搜索历史
        history = db.query(SearchHistory).filter(SearchHistory.id == search_id).first()
        if history:
            history.total_results = len(jobs)
            history.status = "completed"
            db.commit()
        
        logger.info(f"搜索完成，找到 {len(jobs)} 个职位")
        return {"status": "success", "count": len(jobs)}
    
    except Exception as e:
        logger.error(f"搜索失败: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


@celery_app.task
def analyze_jobs_task(min_score: int = 60):
    """分析职位匹配度"""
    logger.info("开始分析职位...")
    
    db = SessionLocal()
    agent = JobSearchAgent()
    
    try:
        # 获取未分析的职位
        jobs = db.query(Job).filter(Job.match_score == 0).all()
        
        for job in jobs[:10]:  # 每次处理10个
            analysis = agent.analyze_job({
                "title": job.title,
                "description": job.description,
                "requirements": job.requirements,
            })
            
            job.match_score = analysis.get("match_score", 0)
            job.is_suitable = analysis.get("is_suitable", False)
            job.analysis = analysis.get("reason", "")
        
        db.commit()
        logger.info(f"分析了 {len(jobs)} 个职位")
        return {"status": "success", "analyzed": len(jobs)}
    
    except Exception as e:
        logger.error(f"分析失败: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


def run_worker():
    """启动 Worker"""
    init_db()
    celery_app.start()


if __name__ == "__main__":
    run_worker()
