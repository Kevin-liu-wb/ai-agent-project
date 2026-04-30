"""主程序入口"""
import os
import sys
import argparse
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import init_db, SessionLocal
from src.models import Job
from src.scraper import MockScraper
from src.agent import JobSearchAgent


def init_command():
    print("正在初始化数据库...")
    init_db()
    print("数据库初始化完成！")


def search_command(keyword: str = "软件工程师", location: str = "上海浦东"):
    print(f"搜索: {keyword} @ {location}")
    
    db = SessionLocal()
    scraper = MockScraper()
    
    jobs = scraper.search_jobs(keyword=keyword, location=location)
    
    for job_data in jobs:
        existing = db.query(Job).filter(Job.job_id == job_data["job_id"]).first()
        if not existing:
            job = Job(**job_data)
            db.add(job)
    
    db.commit()
    print(f"找到 {len(jobs)} 个职位并保存到数据库")


def list_command(status: str = None, min_score: int = 0, limit: int = 20):
    db = SessionLocal()
    query = db.query(Job)
    
    if status:
        query = query.filter(Job.status == status)
    if min_score > 0:
        query = query.filter(Job.match_score >= min_score)
    
    jobs = query.order_by(Job.match_score.desc()).limit(limit).all()
    
    print(f"\n找到 {len(jobs)} 个职位:\n")
    print("ID    职位                      公司                 薪资         匹配分")
    print("-" * 80)
    
    for job in jobs:
        salary = job.salary_text or "面议"
        score = job.match_score or 0
        print(f"{job.id:<5} {job.title[:24]:<25} {job.company[:19]:<20} "
              f"{salary:<12} {score:<8.1f}")


def detail_command(job_id: int):
    db = SessionLocal()
    job = db.query(Job).filter(Job.id == job_id).first()
    
    if not job:
        print(f"未找到职位 ID: {job_id}")
        return
    
    salary_text = job.salary_text or "面议"
    experience_text = job.experience or "不限"
    education_text = job.education or "不限"
    description_text = job.description or "暂无描述"
    requirements_text = job.requirements or "暂无要求"
    analysis_text = job.analysis or "未分析"
    is_suitable_text = "是" if job.is_suitable else "否"
    is_favorite_text = "已收藏" if job.is_favorite else "未收藏"
    
    print("")
    print("=" * 60)
    print(f"职位: {job.title}")
    print(f"公司: {job.company}")
    print(f"地点: {job.location} | 薪资: {salary_text}")
    print(f"经验: {experience_text} | 学历: {education_text}")
    print(f"链接: {job.url}")
    print("")
    print("职位描述:")
    print(description_text)
    print("")
    print("职位要求:")
    print(requirements_text)
    print("")
    print(f"AI 分析: {analysis_text}")
    print(f"匹配分数: {job.match_score or 0}")
    print(f"是否适合: {is_suitable_text}")
    print(f"收藏状态: {is_favorite_text}")
    print("=" * 60)
    print("")


def analyze_command():
    print("开始分析职位匹配度...")
    
    db = SessionLocal()
    agent = JobSearchAgent()
    
    jobs = db.query(Job).filter(Job.match_score == 0).all()
    
    for job in jobs[:10]:
        analysis = agent.analyze_job({
            "title": job.title,
            "description": job.description,
            "requirements": job.requirements,
        })
        
        job.match_score = analysis.get("match_score", 0)
        job.is_suitable = analysis.get("is_suitable", False)
        job.analysis = analysis.get("reason", "")
    
    db.commit()
    print(f"分析了 {len(jobs)} 个职位")


def favorite_command(job_id: int):
    db = SessionLocal()
    job = db.query(Job).filter(Job.id == job_id).first()
    
    if job:
        job.is_favorite = True
        db.commit()
        print(f"已收藏职位: {job.title}")
    else:
        print(f"未找到职位 ID: {job_id}")


def stats_command():
    db = SessionLocal()
    
    total = db.query(Job).count()
    favorites = db.query(Job).filter(Job.is_favorite == True).count()
    high_match = db.query(Job).filter(Job.match_score >= 70).count()
    
    print(f"\n统计信息:")
    print(f"   总职位数: {total}")
    print(f"   已收藏: {favorites}")
    print(f"   高匹配(>=70): {high_match}")


def main():
    parser = argparse.ArgumentParser(description="Kevin 的求职 Agent")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    subparsers.add_parser("init", help="初始化数据库")
    
    search_parser = subparsers.add_parser("search", help="搜索职位")
    search_parser.add_argument("--keyword", default="软件工程师", help="关键词")
    search_parser.add_argument("--location", default="上海浦东", help="地点")
    
    list_parser = subparsers.add_parser("list", help="列出职位")
    list_parser.add_argument("--status", help="状态过滤")
    list_parser.add_argument("--min-score", type=int, default=0, help="最低匹配分数")
    list_parser.add_argument("--limit", type=int, default=20, help="数量限制")
    
    detail_parser = subparsers.add_parser("detail", help="查看职位详情")
    detail_parser.add_argument("job_id", type=int, help="职位ID")
    
    fav_parser = subparsers.add_parser("favorite", help="收藏职位")
    fav_parser.add_argument("job_id", type=int, help="职位ID")
    
    subparsers.add_parser("analyze", help="分析职位匹配度")
    subparsers.add_parser("stats", help="查看统计")
    
    args = parser.parse_args()
    
    if args.command == "init":
        init_command()
    elif args.command == "search":
        search_command(args.keyword, args.location)
    elif args.command == "list":
        list_command(args.status, args.min_score, args.limit)
    elif args.command == "detail":
        detail_command(args.job_id)
    elif args.command == "favorite":
        favorite_command(args.job_id)
    elif args.command == "analyze":
        analyze_command()
    elif args.command == "stats":
        stats_command()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
