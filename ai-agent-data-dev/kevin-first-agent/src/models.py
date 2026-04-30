"""数据库模型"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, JSON
from sqlalchemy.sql import func
from config.database import Base


class Job(Base):
    """职位模型"""
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(100), unique=True, index=True, comment="职位唯一标识")
    title = Column(String(200), comment="职位标题")
    company = Column(String(200), comment="公司名称")
    location = Column(String(200), comment="工作地点")
    salary_min = Column(Integer, comment="最低薪资(K)")
    salary_max = Column(Integer, comment="最高薪资(K)")
    salary_text = Column(String(100), comment="薪资文本")
    experience = Column(String(100), comment="经验要求")
    education = Column(String(50), comment="学历要求")
    description = Column(Text, comment="职位描述")
    requirements = Column(Text, comment="职位要求")
    tags = Column(JSON, comment="职位标签")
    source = Column(String(50), comment="来源网站")
    url = Column(String(500), comment="职位链接")
    
    # 分析字段
    is_suitable = Column(Boolean, default=None, comment="是否匹配")
    match_score = Column(Float, default=0.0, comment="匹配分数")
    analysis = Column(Text, comment="AI 分析结果")
    
    # 状态
    is_applied = Column(Boolean, default=False, comment="是否已投递")
    is_favorite = Column(Boolean, default=False, comment="是否收藏")
    status = Column(String(50), default="new", comment="状态")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SearchHistory(Base):
    """搜索历史"""
    __tablename__ = "search_history"
    
    id = Column(Integer, primary_key=True, index=True)
    keywords = Column(String(200), comment="搜索关键词")
    location = Column(String(200), comment="搜索地点")
    total_results = Column(Integer, comment="结果数量")
    status = Column(String(50), default="running", comment="状态")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))


class AgentLog(Base):
    """Agent 运行日志"""
    __tablename__ = "agent_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_name = Column(String(100), comment="Agent 名称")
    action = Column(String(100), comment="执行动作")
    input_data = Column(JSON, comment="输入数据")
    output_data = Column(JSON, comment="输出数据")
    status = Column(String(50), comment="状态")
    error_message = Column(Text, comment="错误信息")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
