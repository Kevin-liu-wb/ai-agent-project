# Kevin 的求职 Agent

一个基于 Python + LangChain + PostgreSQL + Redis 的智能求职 Agent，可以自动搜索、分析职位匹配度，帮助您高效找工作。

## 功能特性

- 智能职位搜索（支持猎聘网）
- AI 职位匹配分析（基于 OpenAI API）
- 异步任务队列（Celery + Redis）
- 职位收藏与管理
- 数据持久化存储（PostgreSQL）

## 技术栈

| 组件 | 用途 |
|------|------|
| **LangChain / LangGraph** | Agent 编排与 LLM 交互 |
| **PostgreSQL + pgvector** | 数据持久化与向量存储 |
| **Redis** | 缓存与任务队列 |
| **Celery** | 异步任务处理 |
| **BeautifulSoup / Selenium** | Web 抓取 |
| **SQLAlchemy** | ORM 数据库操作 |

## 快速开始

### 1. 环境准备

确保您已经安装并运行了：
- Docker Desktop
- Docker Compose

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，填写您的 OpenAI API Key
```

### 3. 启动服务

使用现有 Docker 网络（推荐，复用您的 ai-agent-project 环境）：

```bash
# 进入项目目录
cd /path/to/kevin-first-agent

# 构建镜像
docker-compose build

# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 4. 初始化数据库

```bash
# 在运行中的容器内执行
docker exec -it kevin-job-agent python -m src.main init
```

## 使用指南

### 命令行操作

```bash
# 1. 搜索职位（软件工程师 @ 上海浦东）
docker exec kevin-job-agent python -m src.main search --keyword "软件工程师" --location "上海浦东"

# 2. 查看搜索的职位列表
docker exec kevin-job-agent python -m src.main list

# 3. 分析职位匹配度（需要配置 OpenAI Key）
docker exec kevin-job-agent python -m src.main analyze

# 4. 查看高匹配职位（分数 ≥ 70）
docker exec kevin-job-agent python -m src.main list --min-score 70

# 5. 查看职位详情
docker exec kevin-job-agent python -m src.main detail 1

# 6. 收藏职位
docker exec kevin-job-agent python -m src.main favorite 1

# 7. 查看统计信息
docker exec kevin-job-agent python -m src.main stats
```

### API 调用示例

```python
from src.agent import JobSearchAgent
from src.scraper import MockScraper

# 1. 创建 Agent
agent = JobSearchAgent()

# 2. 抓取职位
scraper = MockScraper()
jobs = scraper.search_jobs(
    keyword="软件工程师",
    location="上海浦东"
)

# 3. 分析匹配度
for job in jobs:
    result = agent.analyze_job(job)
    print(f"{job[title]}: 匹配度 {result[match_score]}%")
```

## 项目结构

```
kevin-first-agent/
├── config/                 # 配置文件
│   ├── database.py        # PostgreSQL 配置
│   └── redis_client.py     # Redis 客户端
├── src/
│   ├── models.py           # 数据库模型
│   ├── scraper.py          # 网页抓取器
│   ├── agent.py            # Agent 核心逻辑
│   ├── worker.py           # Celery 任务
│   └── main.py             # CLI 入口
├── tests/                  # 测试文件
├── requirements.txt        # Python 依赖
├── docker-compose.yml      # Docker 编排
├── Dockerfile              # 容器镜像
└── README.md              # 本文件
```

## 数据库模型

### Job（职位表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| job_id | String | 职位唯一标识 |
| title | String | 职位标题 |
| company | String | 公司名称 |
| location | String | 工作地点 |
| salary_min/max | Integer | 薪资范围 |
| description | Text | 职位描述 |
| match_score | Float | 匹配分数 |
| is_suitable | Boolean | 是否适合 |
| analysis | Text | AI 分析结果 |
| is_favorite | Boolean | 是否收藏 |
| status | String | 状态 |

## 扩展功能

### 切换真实抓取器

修改 `src/worker.py`：

```python
# 使用真实猎聘网抓取（需要处理反爬和登录）
from src.scraper import LiepinScraper
scraper = LiepinScraper()

# 或使用模拟数据（测试用）
from src.scraper import MockScraper
scraper = MockScraper()
```

### 添加更多数据源

在 `src/scraper.py` 中实现新的抓取器：

```python
class BossScraper:
    """BOSS直聘抓取器"""
    def search_jobs(self, keyword, location):
        # 实现抓取逻辑
        pass
```

## 注意事项

1. **Web 抓取限制**：猎聘网等招聘网站可能有反爬虫机制，抓取时请注意：
   - 控制请求频率
   - 可能需要登录态
   - 使用代理 IP

2. **OpenAI 费用**：职位分析需要调用 OpenAI API，注意控制请求量

3. **数据隐私**：抓取到的职位数据仅供个人学习使用

## 学习路径

通过这个 Agent，您可以学习：

1. **Agent 架构设计** - 如何构建任务驱动的 AI Agent
2. **LangChain 使用** - Prompt 工程、工具调用、链式编排
3. **异步任务处理** - Celery + Redis 实现分布式任务
4. **数据库设计** - SQLAlchemy ORM 和模型设计
5. **Web 抓取** - requests + BeautifulSoup 数据抓取

## 常见问题

### Q: 如何连接 Dify？
A: 已安装 `dify-client`，可在 `src/agent.py` 中添加 Dify API 调用：

```python
from dify_client import ChatClient

client = ChatClient(api_key="your-key")
client.create_chat_message(inputs={}, query="分析职位", user="kevin")
```

### Q: 数据库连接失败？
A: 确保 PostgreSQL 服务已启动，检查 `.env` 中的连接配置。

### Q: 如何使用本地 LLM？
A: 修改 `src/agent.py`，配置本地 vLLM 或 Ollama：

```python
from langchain_community.llms import Ollama
llm = Ollama(base_url="http://localhost:11434", model="llama2")
```

## 许可证

MIT License - 仅供学习使用
