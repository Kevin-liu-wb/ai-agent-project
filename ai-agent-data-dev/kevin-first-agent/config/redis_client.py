"""Redis 客户端配置"""
import os
import redis
from typing import Optional

REDIS_HOST = os.getenv("REDIS_HOST", "ai-agent-redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=True
)


def get_redis():
    """获取 Redis 客户端"""
    return redis_client


def cache_job(job_id: str, job_data: dict, expire: int = 3600):
    """缓存职位信息"""
    import json
    redis_client.setex(f"job:{job_id}", expire, json.dumps(job_data))


def get_cached_job(job_id: str) -> Optional[dict]:
    """获取缓存的职位信息"""
    import json
    data = redis_client.get(f"job:{job_id}")
    return json.loads(data) if data else None


def add_to_queue(queue_name: str, data: dict):
    """添加任务到队列"""
    import json
    redis_client.lpush(f"queue:{queue_name}", json.dumps(data))


def pop_from_queue(queue_name: str) -> Optional[dict]:
    """从队列获取任务"""
    import json
    data = redis_client.brpop(f"queue:{queue_name}", timeout=5)
    if data:
        return json.loads(data[1])
    return None
