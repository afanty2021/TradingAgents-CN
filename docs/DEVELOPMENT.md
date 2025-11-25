# TradingAgents-CN 开发指南

## 🎯 项目概述

TradingAgents-CN 是一个基于多智能体协作的金融分析系统，采用现代化微服务架构，支持本地开发和云端部署。

### 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────┐
│                    Web Interface Layer           │
│  ┌─────────────┬───────────────────────────┐ │
│  │ Streamlit App│  Vue.js Frontend     │
│  └─────────────┴───────────────────────────┘ │
├─────────────────────────────────────────────────────┤
│                API Gateway Layer              │
│  ┌─────────────┬───────────────────────────┐ │
│  │ FastAPI     │  REST Endpoints      │
│  └─────────────┴───────────────────────────┘ │
├─────────────────────────────────────────────────────┤
│              Core Business Logic             │
│  ┌─────────────┬───────────────────────────┐ │
│  │ Multi-Agent │  Analysis Engine     │
│  └─────────────┴───────────────────────────┘ │
├─────────────────────────────────────────────────────┤
│               Data & Caching Layer          │
│  ┌─────────────┬───────────────────────────┐ │
│  │   MongoDB   │      Redis           │
│  └─────────────┴───────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

### 🔧 技术栈

#### 后端
- **Python**: 3.10+ (推荐 3.11)
- **Web框架**: FastAPI 0.104+
- **AI框架**: LangChain 0.1+
- **数据库**: MongoDB 6.0+
- **缓存**: Redis 7.0+
- **异步**: asyncio + uvicorn
- **类型检查**: mypy + pydantic

#### 前端
- **Streamlit**: 1.28+ (管理界面)
- **Vue.js**: 3.3+ (用户界面)
- **TypeScript**: 5.0+
- **构建工具**: Vite 5.0+

#### 部署
- **容器化**: Docker + Docker Compose
- **反向代理**: Nginx (可选)
- **监控**: Prometheus + Grafana (可选)

## 🚀 快速开始

### 环境要求

```bash
# Python版本检查
python --version  # >= 3.10

# 系统依赖
curl --version      # >= 7.68
docker --version     # >= 20.10
git --version       # >= 2.30
```

### 本地开发环境

#### 1. 克隆项目
```bash
# 克隆主仓库
git clone https://github.com/hsliuping/TradingAgents-CN.git
cd TradingAgents-CN

# 或Fork后克隆
git clone https://github.com/YOUR_USERNAME/TradingAgents-CN.git
cd TradingAgents-CN
git remote add upstream https://github.com/hsliuping/TradingAgents-CN.git
```

#### 2. 设置Python环境
```bash
# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或 Windows
venv\Scripts\activate

# 升级pip
pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt

# 安装开发依赖
pip install -r requirements-dev.txt
```

#### 3. 配置环境变量
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量
nano .env
```

**必需的环境变量：**
```bash
# AI模型API密钥
DASHSCOPE_API_KEY=sk-your-dashscope-key
DEEPSEEK_API_KEY=sk-your-deepseek-key
OPENAI_API_KEY=sk-your-openai-key
GOOGLE_API_KEY=your-google-api-key

# 数据源API密钥
FINNHUB_API_KEY=your-finnhub-key
TUSHARE_TOKEN=your-tushare-token

# 数据库配置（可选）
MONGODB_ENABLED=true
REDIS_ENABLED=true
MONGODB_URL=mongodb://localhost:27017/tradingagents
REDIS_URL=redis://localhost:6379/0

# 应用配置
ENVIRONMENT=development
DEBUG_MODE=true
LOG_LEVEL=DEBUG
```

#### 4. 初始化数据库
```bash
# 启动数据库服务
docker-compose up -d mongodb redis

# 等待服务启动
sleep 5

# 初始化数据库
python scripts/setup/initialize_databases.py

# 检查数据库状态
python scripts/development/check_database_status.py
```

#### 5. 启动开发服务器
```bash
# 方式1: 使用启动脚本（推荐）
python start_web.py

# 方式2: 直接启动API服务器
uvicorn web.api.main:app --reload --host 0.0.0.0 --port 8501

# 方式3: 启动完整服务栈
docker-compose -f docker-compose.dev.yml up
```

### 验证安装
```bash
# 运行安装验证
python scripts/development/verify_installation.py

# 检查API健康状态
curl -X GET "http://localhost:8501/api/v1/health" \
     -H "Content-Type: application/json"

# 运行基础测试
pytest tests/unit/test_financial_analyzer.py -v
```

## 🛠️ 开发工作流

### Git工作流

#### 分支策略
```bash
# 主分支
main                    # 生产代码
develop                 # 开发分支
feature/feature-name    # 功能分支
hotfix/issue-number    # 热修复分支
release/vX.X.X         # 发布分支
```

#### 提交规范
```bash
# 提交信息格式
<type>(<scope>): <subject>

# 类型说明
feat:     新功能
fix:      修复bug
docs:     文档更新
style:    代码格式化
refactor:  代码重构
test:     测试相关
chore:    构建过程或辅助工具的变动

# 示例
feat(api): add WebSocket support for real-time analysis
fix(cache): resolve memory leak in cache manager
docs(readme): update installation guide
```

#### 代码审查
```bash
# 使用内置代码审查工具
python scripts/development/code_review.py

# 或使用GitHub CLI
gh pr create --title "Add WebSocket support" --head main

# 提交前检查
python scripts/development/pre_commit_check.py
```

### 测试策略

#### 测试类型
```bash
# 单元测试
pytest tests/unit/ -v --cov=tradingagents

# 集成测试
pytest tests/integration/ -v

# API测试
pytest tests/api/ -v --api

# 性能测试
pytest tests/performance/ -v --benchmark

# 端到端测试
pytest tests/e2e/ -v
```

#### 测试命令
```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试文件
pytest tests/unit/test_financial_analyzer.py -v

# 运行带标记的测试
pytest tests/ -m "unit" -v

# 生成覆盖率报告
pytest tests/ --cov=tradingagents --cov-report=html

# 监听文件变化并自动运行测试
pytest-watch tests/ -v
```

## 🏗️ 代码结构

### 项目目录结构
```
TradingAgents-CN/
├── tradingagents/           # 核心业务逻辑
│   ├── agents/              # 智能体模块
│   │   ├── analysts/       # 分析师团队
│   │   ├── managers/      # 管理层
│   │   └── researchers/   # 研究员
│   ├── graph/              # 工作流引擎
│   ├── dataflows/          # 数据流模块
│   ├── llm_adapters/      # LLM适配器
│   ├── performance/        # 性能优化模块
│   ├── security/           # 安全模块
│   └── utils/             # 工具模块
├── web/                   # Web应用
│   ├── api/               # FastAPI REST API
│   ├── components/         # Vue.js组件
│   ├── utils/              # Web工具模块
│   └── static/             # 静态资源
├── tests/                 # 测试套件
│   ├── unit/               # 单元测试
│   ├── integration/        # 集成测试
│   ├── api/                # API测试
│   ├── performance/         # 性能测试
│   └── e2e/                # 端到端测试
├── docs/                  # 文档
│   ├── api/                # API文档
│   ├── development/         # 开发指南
│   └── deployment/         # 部署指南
├── scripts/               # 脚本工具
│   ├── development/         # 开发工具
│   ├── deployment/          # 部署脚本
│   └── maintenance/         # 维护工具
├── config/                # 配置文件
├── docker/                 # Docker配置
└── requirements/           # 依赖管理
```

### 核心模块说明

#### 智能体系统 (tradingagents/agents/)
```python
# 分析师基类
class BaseAnalyst:
    def __init__(self, llm, toolkit, config):
        self.llm = llm
        self.toolkit = toolkit
        self.config = config

    def analyze(self, state):
        raise NotImplementedError

# 具体分析师实现
class MarketAnalyst(BaseAnalyst):
    """市场技术分析师"""
    def analyze(self, state):
        # 技术指标分析
        pass

class FundamentalsAnalyst(BaseAnalyst):
    """基本面分析师"""
    def analyze(self, state):
        # 财务数据分析
        pass
```

#### 工作流引擎 (tradingagents/graph/)
```python
# 主工作流图
class TradingAgentsGraph:
    def __init__(self, config):
        self.graph = self._build_graph()
        self.config = config

    def propagate(self, symbol, date):
        # 执行完整分析流程
        pass
```

## 🔧 开发工具

### IDE配置

#### VS Code配置
```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "python.sortImports.args": ["--profile", "black"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

#### PyCharm配置
```xml
<!-- .idea/inspectionProfiles/Project_Default.xml -->
<component name="InspectionProjectProfileManager">
    <profile version="1.0">
        <option name="myName" value="Project Default" />
        <inspection_tool class="PyPep8Inspection" enabled="true" level="WEAK WARNING" enabled_by_default="true">
            <option name="ignoredErrors">
                <list>
                    <option value="E501" />
                </list>
            </option>
        </inspection_tool>
    </profile>
</component>
```

### 调试配置

#### VS Code调试
```json
// .vscode/launch.json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: TradingAgents",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/venv/bin/python",
            "args": ["start_web.py"],
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}",
            "env": {
                "PYTHONPATH": "${workspaceFolder}/venv/bin"
            }
        }
    ]
}
```

#### 日志配置
```python
# logging_config.py
import logging

DEVELOPMENT_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'detailed': {
            'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(funcName)s() %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'detailed',
            'filename': 'logs/tradingagents-dev.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'encoding': 'utf8'
        }
    },
    'loggers': {
        '': {
            'level': 'DEBUG',
            'handlers': ['console', 'file']
        },
        'tradingagents': {
            'level': 'DEBUG',
            'handlers': ['console', 'file'],
            'propagate': False
        }
    }
}
```

## 🧪 测试开发

### 编写测试

#### 单元测试示例
```python
# tests/unit/test_financial_analyzer.py
import pytest
from tradingagents.agents.analysts.fundamentals.financial_analyzer import FinancialAnalyzer

class TestFinancialAnalyzer:
    def setup_method(self):
        """测试前准备"""
        self.analyzer = FinancialAnalyzer()
        self.mock_data = {
            'revenue': {'2023': 1000.0},
            'net_income': {'2023': 100.0},
            'total_assets': {'2023': 2000.0},
            'shareholders_equity': {'2023': 1000.0},
            'total_debt': {'2023': 500.0}
        }

    def test_calculate_roe(self):
        """测试ROE计算"""
        roe = self.analyzer._calculate_roe(self.mock_data, '2023')
        assert roe == 10.0  # (100 / 1000) * 100

    @pytest.mark.parametrize("input_data,expected", [
        ({'revenue': 1000, 'net_income': 100}, 10.0),
        ({'revenue': 2000, 'net_income': 200}, 10.0),
    ])
    def test_roe_with_different_data(self, input_data, expected):
        """参数化测试ROE计算"""
        data = FinancialData(**input_data)
        roe = self.analyzer._calculate_roe(data, '2023')
        assert roe == expected
```

#### Mock和Fixture
```python
# tests/conftest.py
import pytest
from unittest.mock import Mock

@pytest.fixture
def mock_llm_response():
    """模拟LLM响应"""
    mock_response = Mock()
    mock_response.content = "Mock analysis result"
    return mock_response

@pytest.fixture
def sample_stock_data():
    """示例股票数据"""
    return {
        'symbol': 'AAPL',
        'price': 150.0,
        'volume': 50000000,
        'market_cap': 3000000000000
    }
```

### API测试
```python
# tests/api/test_analysis.py
import pytest
from fastapi.testclient import TestClient

def test_analysis_endpoint(client):
    """测试分析端点"""
    response = client.post(
        "/api/v1/analysis/start",
        json={
            "symbol": "AAPL",
            "analysis_date": "2024-01-15",
            "analysts": ["market_analyst", "fundamentals_analyst"],
            "research_depth": 3
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "analysis_id" in data["data"]
```

### 性能测试
```python
# tests/performance/test_cache_performance.py
import pytest
import time

def test_cache_performance():
    """测试缓存性能"""
    cache = SmartCacheManager(max_memory_size=100*1024*1024)

    # 测试写入性能
    start_time = time.time()
    for i in range(1000):
        cache.set(f"key_{i}", f"value_{i}")
    write_time = time.time() - start_time

    # 测试读取性能
    start_time = time.time()
    for i in range(1000):
        value = cache.get(f"key_{i}")
    read_time = time.time() - start_time

    # 验证性能要求
    assert write_time < 1.0, f"写入性能: {write_time:.3f}s"
    assert read_time < 0.5, f"读取性能: {read_time:.3f}s"
```

## 🔒 安全开发

### 密钥管理
```python
# 使用安全密钥管理器
from tradingagents.security.secure_key_manager import SecureKeyManager

# 初始化
key_manager = SecureKeyManager()

# 存储API密钥
key_manager.store_key('dashscope', 'sk-your-actual-key', metadata={'provider': 'dashscope'})

# 获取API密钥
api_key = key_manager.get_key('dashscope')

# 轮换密钥
new_key = 'sk-new-key-here'
key_manager.rotate_key('dashscope', new_key)

# 审计密钥使用
audit_info = key_manager.audit_keys()
```

### 输入验证
```python
# 使用Pydantic进行输入验证
from pydantic import BaseModel, Field, validator
from typing import Optional

class AnalysisRequest(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=10, regex=r'^[A-Z0-9\.]+$')
    analysis_date: str = Field(..., regex=r'^\d{4}-\d{2}-\d{2}$')
    analysts: list[str] = Field(default_factory=lambda: ["market_analyst"])
    research_depth: int = Field(default=3, ge=1, le=5)
    market_type: str = Field(default="美股", regex=r'^(美股|A股|港股)$')

    @validator('symbol')
    def validate_symbol(cls, v):
        return v.upper()

# 使用示例
try:
    request = AnalysisRequest(**request_data)
except ValidationError as e:
    print(f"输入验证错误: {e}")
```

### 依赖安全
```bash
# 检查依赖漏洞
pip audit

# 使用SAST工具
bandit -r tradingagents/

# 检查密钥泄露
git-secrets --all

# 依赖许可检查
pip-licenses --from=mixin --format=csv > licenses.csv
```

## 🚀 部署开发

### Docker开发环境
```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  tradingagents-api:
    build:
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - "8501:8501"
    environment:
      - ENVIRONMENT=development
      - DEBUG_MODE=true
      - LOG_LEVEL=DEBUG
    volumes:
      - ./tradingagents:/app
      - ./logs:/app/logs
      - ./data:/app/data
    depends_on:
      - mongodb
      - redis

  mongodb:
    image: mongo:6.0
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  mongodb_data:
  redis_data:
```

### 生产环境配置
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  tradingagents-api:
    image: tradingagents-cn:latest
    ports:
      - "8501:8501"
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=INFO
      - DEBUG_MODE=false
    volumes:
      - ./logs:/app/logs
      - ./config:/app/config
    depends_on:
      - mongodb
      - redis
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
```

### CI/CD配置
```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.10, 3.11]

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Run linting
        run: |
          black --check tradingagents/
          flake8 tradingagents/
          mypy tradingagents/

      - name: Run tests
        run: |
          pytest tests/ -v --cov=tradingagents --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

## 📚 文档生成

### API文档生成
```bash
# 自动生成OpenAPI文档
uvicorn web.api.main:app --reload --host 0.0.0.0 --port 8501

# 访问Swagger UI
open http://localhost:8501/docs

# 导出OpenAPI规范
curl -X GET "http://localhost:8501/openapi.json" > openapi.json
```

### 代码文档生成
```bash
# 生成模块文档
pdoc tradingagents.agents.analysts.fundamentals -o docs/api/fundamentals.html

# 生成完整项目文档
pdoc tradingagents -o docs/index.html

# 生成API客户端代码
openapi-generator generate -i openapi.json -g python -o clients/python/
```

## 🔍 调试技巧

### 日志调试
```python
import logging

# 设置详细日志
logging.basicConfig(level=logging.DEBUG)

# 模块特定日志
logger = logging.getLogger(__name__)
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

### 性能分析
```python
import cProfile
import pstats

# 性能分析
def profile_function(func):
    def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()

        result = func(*args, **kwargs)

        profiler.disable()

        stats = pstats.Stats(profiler)
        stats.sort_stats('cumulative')
        stats.print_stats(10)

        return result
    return wrapper

# 使用装饰器
@profile_function
def expensive_function():
    # 复杂计算逻辑
    pass
```

### 内存分析
```python
import tracemalloc
import gc

# 内存泄漏检测
def detect_memory_leaks():
    tracemalloc.start()

    # 执行可能泄漏的代码
    gc.collect()

    snapshot1 = tracemalloc.take_snapshot()

    # 更多代码...

    gc.collect()
    snapshot2 = tracemalloc.take_snapshot()

    # 比较快照
    stats = snapshot2.compare_to(snapshot1)

    for stat in stats:
        if stat.count_diff > 0:
            print(f"Memory leak detected: {stat}")
```

## 🛠️ 常见问题

### 环境配置问题
```bash
# 问题：模块导入错误
ModuleNotFoundError: No module named 'tradingagents'

# 解决：检查Python路径和虚拟环境
which python
echo $PYTHONPATH
source venv/bin/activate

# 问题：API密钥未配置
AuthenticationError: API key not configured

# 解决：检查环境变量
echo $DASHSCOPE_API_KEY
cat .env

# 问题：数据库连接失败
ConnectionError: Cannot connect to MongoDB

# 解决：检查数据库服务
docker ps
docker-compose logs mongodb
```

### 依赖冲突
```bash
# 问题：版本冲突
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed

# 解决：使用虚拟环境
pip uninstall -y conflicting-package
pip install -r requirements.txt

# 问题：缓存不工作
CacheError: Redis connection failed

# 解决：检查Redis服务
redis-cli ping
docker-compose logs redis
```

### 性能问题
```python
# 问题：内存泄漏
MemoryError: Unable to allocate array

# 解决：使用生成器和限制数据大小
def generate_large_data():
    for chunk in generate_data_in_chunks():
        yield chunk

# 问题：响应缓慢
TimeoutError: Request timeout

# 解决：使用异步和缓存
import asyncio
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_calculation(data):
    # 缓存计算结果
    pass
```

## 📈 性能优化指南

### 代码优化
```python
# 使用生成器表达式
def process_large_file(filename):
    with open(filename) as f:
        for line in f:  # 逐行处理，不加载整个文件
            yield process_line(line)

# 使用内置函数
def calculate_statistics(data):
    return {
        'mean': sum(data) / len(data),
        'min': min(data),
        'max': max(data),
        'std': (sum((x - sum(data)/len(data))**2 for x in data) / len(data))**0.5
    }

# 避免不必要的循环
def find_duplicates(items):
    seen = set()
    duplicates = []
    for item in items:
        if item in seen:
            duplicates.append(item)
        seen.add(item)
    return duplicates
```

### 数据库优化
```python
# 使用索引
db.analysis_results.create_index([("stock_symbol", "analysis_date")])
db.analysis_results.create_index([("user_id", "created_at")])

# 使用批量操作
def bulk_insert_data(data_list):
    db.analysis_results.insert_many(data_list)

# 使用连接池
from pymongo import MongoClient

client = MongoClient(
    maxPoolSize=10,
    minPoolSize=2
)
```

### 缓存策略
```python
# 智能缓存
from tradingagents.performance.smart_cache import SmartCacheManager

cache = SmartCacheManager(
    max_memory_size=100*1024*1024,  # 100MB
    strategy=CacheStrategy.ADAPTIVE
)

# 缓存热数据
@cache.cache_result(ttl=3600)  # 1小时
def expensive_api_call(api_params):
    # API调用逻辑
    pass

# 预加载常用数据
def preload_common_data():
    common_symbols = ['AAPL', 'MSFT', 'GOOGL']
    for symbol in common_symbols:
        cache.set(f"stock_basic_{symbol}", get_stock_basic_info(symbol))
```

## 🔄 持续集成

### 自动化测试
```bash
# 设置pre-commit钩子
pre-commit install

# 添加配置到.pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: black
        entry: black
        language: system
        files: \.py$
      - id: flake8
        entry: flake8
        language: system
        files: \.py$
```

### 代码质量监控
```yaml
# .github/workflows/quality.yml
name: Code Quality

on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run Black
        run: black --check --diff tradingagents/

      - name: Run Flake8
        run: flake8 tradingagents/ --count --select=E9,F63,F7,F6 --show-source --statistics

      - name: Run MyPy
        run: mypy tradingagents/ --ignore-missing-imports
```

## 📚 推荐资源

### 学习资源
- [Python官方文档](https://docs.python.org/3/)
- [FastAPI文档](https://fastapi.tiangolo.com/)
- [LangChain文档](https://python.langchain.com/)
- [Pydantic文档](https://pydantic-docs.helpmanual.io/)
- [Docker文档](https://docs.docker.com/)

### 开发工具
- [VS Code](https://code.visualstudio.com/)
- [PyCharm](https://www.jetbrains.com/pycharm/)
- [Postman](https://www.postman.com/)
- [DBeaver](https://dbeaver.io/)

### 社区资源
- [GitHub](https://github.com/hsliuping/TradingAgents-CN)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/tradingagents-cn)
- [Reddit](https://www.reddit.com/r/TradingAgents/)

## 🤝 贡献指南

请参考 [CONTRIBUTING.md](CONTRIBUTING.md) 了解如何为项目贡献代码。

## 📞 支持渠道

- [GitHub Issues](https://github.com/hsliuping/TradingAgents-CN/issues)
- [讨论区](https://github.com/hsliuping/TradingAgents-CN/discussions)
- [项目Wiki](https://github.com/hsliuping/TradingAgents-CN/wiki)
- [QQ群](187537480)

---

*最后更新：2025-01-25*
*版本：v1.0.0*