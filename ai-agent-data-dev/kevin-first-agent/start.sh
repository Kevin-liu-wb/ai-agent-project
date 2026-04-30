#!/bin/bash
# 快速启动脚本

set -e

echo "🚀 启动 Kevin 的求职 Agent..."

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "⚠️  未找到 .env 文件，复制模板..."
    cp .env.example .env
    echo "📝 请编辑 .env 文件，添加您的 OpenAI API Key"
fi

# 启动服务
echo "🐳 启动 Docker 服务..."
docker-compose up -d

echo "⏳ 等待数据库就绪..."
sleep 5

# 初始化数据库
echo "📊 初始化数据库..."
docker exec -it kevin-job-agent python -m src.main init || echo "数据库可能已初始化"

echo ""
echo "✅ 启动完成！可用命令："
echo ""
echo "  # 搜索职位"
echo "  docker exec kevin-job-agent python -m src.main search --keyword 软件工程师 --location 上海浦东"
echo ""
echo "  # 列出职位"
echo "  docker exec kevin-job-agent python -m src.main list"
echo ""
echo "  # 分析匹配度"
echo "  docker exec kevin-job-agent python -m src.main analyze"
echo ""
echo "  # 查看统计"
echo "  docker exec kevin-job-agent python -m src.main stats"
echo ""
echo "📝 查看日志: docker-compose logs -f"
echo "🛑 停止服务: docker-compose down"
