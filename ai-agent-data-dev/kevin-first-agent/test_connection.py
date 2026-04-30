"""测试数据库和 Redis 连接"""
import sys
sys.path.insert(0, /app)

print("测试环境连接...")

try:
    from sqlalchemy import create_engine, text
    from config.database import DATABASE_URL
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("✅ PostgreSQL 连接成功")
except Exception as e:
    print(f"❌ PostgreSQL 连接失败: {e}")

try:
    from config.redis_client import redis_client
    redis_client.set("test", "ok", ex=5)
    print("✅ Redis 连接成功")
except Exception as e:
    print(f"❌ Redis 连接失败: {e}")
