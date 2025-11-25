# TradingAgents-CN API 文档

## 概览

TradingAgents-CN 提供了完整的REST API和Python SDK，支持多智能体金融分析、实时数据处理和用户管理功能。

**API版本**: v1.0.0
**基础URL**: `http://localhost:8501/api/v1`
**认证方式**: Bearer Token / API Key
**数据格式**: JSON
**字符编码**: UTF-8

## 快速开始

### 1. 环境配置

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑配置文件
nano .env
```

### 2. 安装依赖

```bash
# 安装Python依赖
pip install -r requirements.txt

# 启动服务
python start_web.py
```

### 3. 首次请求

```bash
# 测试API连接
curl -X GET "http://localhost:8501/api/v1/health" \
     -H "Authorization: Bearer YOUR_API_KEY"
```

## 核心API端点

### 🔐 认证相关

#### 用户登录
```http
POST /api/v1/auth/login
```

**请求体**:
```json
{
  "username": "your_username",
  "password": "your_password"
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "user_id": "user_123",
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "expires_at": "2024-01-15T10:30:00Z",
    "permissions": [
      "stock_analysis",
      "report_export"
    ],
    "role": "user"
  },
  "message": "登录成功"
}
```

#### 刷新令牌
```http
POST /api/v1/auth/refresh
```

**请求头**:
```
Authorization: Bearer REFRESH_TOKEN
```

**响应**:
```json
{
  "success": true,
  "data": {
    "token": "new_access_token",
    "expires_at": "2024-01-15T10:30:00Z"
  }
}
```

### 📊 股票分析

#### 启动分析
```http
POST /api/v1/analysis/start
```

**请求头**:
```
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json
```

**请求体**:
```json
{
  "symbol": "AAPL",
  "analysis_date": "2024-01-15",
  "analysts": [
    "market_analyst",
    "fundamentals_analyst",
    "news_analyst",
    "social_media_analyst"
  ],
  "research_depth": 3,
  "market_type": "美股",
  "config": {
    "llm_provider": "dashscope",
    "model": "qwen-plus",
    "enable_cache": true,
    "max_debate_rounds": 3
  }
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "analysis_id": "analysis_123456",
    "status": "started",
    "estimated_duration": 300,
    "queue_position": 1
  },
  "message": "分析已启动"
}
```

#### 获取分析状态
```http
GET /api/v1/analysis/{analysis_id}/status
```

**响应**:
```json
{
  "success": true,
  "data": {
    "analysis_id": "analysis_123456",
    "status": "completed",
    "progress": 100,
    "current_step": "交易决策",
    "total_steps": 9,
    "started_at": "2024-01-15T10:00:00Z",
    "completed_at": "2024-01-15T10:05:00Z",
    "results": {
      "recommendation": "买入",
      "confidence": 78,
      "target_price": 165.50,
      "risk_level": "medium",
      "holding_period": "6-12个月"
    }
  }
}
```

#### 获取分析结果
```http
GET /api/v1/analysis/{analysis_id}/results
```

**查询参数**:
- `format`: `json` | `html` | `pdf` (默认: json)
- `include_details`: `true` | `false` (默认: false)
- `section`: `summary` | `detailed` | `analyst_reports` (可选)

**响应**:
```json
{
  "success": true,
  "data": {
    "basic_info": {
      "symbol": "AAPL",
      "company_name": "苹果公司",
      "market": "美股",
      "sector": "科技",
      "current_price": 150.20
    },
    "investment_recommendation": {
      "action": "买入",
      "confidence": 78,
      "target_price": 165.50,
      "upside_potential": 10.2,
      "risk_level": "medium",
      "holding_period": "6-12个月"
    },
    "financial_analysis": {
      "profitability_score": 82,
      "financial_health_score": 76,
      "efficiency_score": 71,
      "growth_score": 85,
      "valuation_score": 78,
      "key_ratios": {
        "roe": 18.5,
        "net_margin": 12.3,
        "debt_to_equity": 0.45,
        "pe_ratio": 22.3
      }
    },
    "analyst_reports": {
      "market_analyst": {
        "recommendation": "买入",
        "confidence": 75,
        "technical_indicators": {
          "rsi": 65.5,
          "macd": 0.12,
          "bollinger_position": "upper"
        }
      },
      "fundamentals_analyst": {
        "recommendation": "买入",
        "confidence": 80,
        "financial_ratios": {
          "roe": 18.5,
          "pe_ratio": 22.3,
          "debt_to_equity": 0.45
        }
      }
    },
    "risk_assessment": {
      "risk_level": "medium",
      "risk_factors": [
        "市场波动风险",
        "估值回调风险"
      ],
      "mitigating_factors": [
        "盈利能力良好",
        "现金流充足"
      ]
    }
  }
}
```

### 📈 市场数据

#### 获取股票基本信息
```http
GET /api/v1/market/stock/{symbol}
```

**查询参数**:
- `market`: `us` | `china` | `hk` (自动检测)
- `fields`: `basic` | `detailed` | `financial` (默认: basic)

**响应**:
```json
{
  "success": true,
  "data": {
    "symbol": "AAPL",
    "name": "苹果公司",
    "sector": "科技",
    "market": "美股",
    "current_price": 150.20,
    "change": 2.30,
    "change_percent": 1.55,
    "volume": 50000000,
    "market_cap": 3000000000000,
    "pe_ratio": 22.3,
    "dividend_yield": 0.50
  }
}
```

#### 获取历史数据
```http
GET /api/v1/market/stock/{symbol}/history
```

**查询参数**:
- `period`: `1d` | `1w` | `1m` | `3m` | `6m` | `1y` | `5y` (默认: 1y)
- `start_date`: `YYYY-MM-DD` (可选)
- `end_date`: `YYYY-MM-DD` (可选)

**响应**:
```json
{
  "success": true,
  "data": {
    "symbol": "AAPL",
    "period": "1y",
    "prices": [
      {
        "date": "2024-01-15",
        "open": 148.50,
        "high": 151.20,
        "low": 147.80,
        "close": 150.20,
        "volume": 45000000,
        "adj_close": 150.20
      }
      // ... 更多数据点
    ]
  }
}
```

### 📰 新闻分析

#### 获取相关新闻
```http
GET /api/v1/news/{symbol}
```

**查询参数**:
- `limit`: 数量限制 (默认: 10, 最大: 50)
- `sort`: `date` | `relevance` (默认: date)
- `sentiment`: `all` | `positive` | `negative` | `neutral` (默认: all)

**响应**:
```json
{
  "success": true,
  "data": {
    "symbol": "AAPL",
    "total_news": 25,
    "sentiment_summary": {
      "positive": 12,
      "negative": 3,
      "neutral": 10,
      "overall": "positive"
    },
    "articles": [
      {
        "id": "news_123",
        "title": "苹果发布超预期财报",
        "source": "财经头条",
        "url": "https://example.com/news/123",
        "published_at": "2024-01-15T09:00:00Z",
        "sentiment": "positive",
        "relevance_score": 0.95,
        "summary": "苹果公司第四季度财报超出市场预期..."
      }
      // ... 更多新闻
    ]
  }
}
```

### 👥 用户管理

#### 获取用户信息
```http
GET /api/v1/user/profile
```

**请求头**:
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

**响应**:
```json
{
  "success": true,
  "data": {
    "user_id": "user_123",
    "username": "john_doe",
    "role": "user",
    "permissions": [
      "stock_analysis",
      "report_export",
      "config_management"
    ],
    "subscription": {
      "plan": "pro",
      "expires_at": "2024-12-31",
      "analysis_quota": {
        "daily": 100,
        "monthly": 3000,
        "used_daily": 15,
        "used_monthly": 450
      }
    },
    "preferences": {
      "language": "zh-CN",
      "timezone": "Asia/Shanghai",
      "default_analysts": [
        "market_analyst",
        "fundamentals_analyst",
        "news_analyst"
      ]
    }
  }
}
```

#### 更新用户配置
```http
PUT /api/v1/user/preferences
```

**请求体**:
```json
{
  "language": "en-US",
  "timezone": "America/New_York",
  "default_analysts": [
    "market_analyst",
    "fundamentals_analyst",
    "news_analyst",
    "social_media_analyst"
  ],
  "notifications": {
    "email": true,
    "analysis_complete": true,
    "price_alert": true
  }
}
```

### 📋 报告管理

#### 获取历史分析
```http
GET /api/v1/reports/history
```

**查询参数**:
- `page`: 页码 (默认: 1)
- `limit`: 每页数量 (默认: 20, 最大: 100)
- `status`: `completed` | `failed` | `all` (默认: completed)
- `symbol`: 过滤股票代码 (可选)

**响应**:
```json
{
  "success": true,
  "data": {
    "total": 156,
    "page": 1,
    "limit": 20,
    "total_pages": 8,
    "reports": [
      {
        "analysis_id": "analysis_123",
        "symbol": "AAPL",
        "status": "completed",
        "created_at": "2024-01-15T10:05:00Z",
        "recommendation": "买入",
        "confidence": 78,
        "target_price": 165.50,
        "actual_price": 150.20,
        "performance": "+10.2%",
        "holding_period": 45
      }
      // ... 更多报告
    ]
  }
}
```

#### 导出报告
```http
GET /api/v1/reports/{analysis_id}/export
```

**查询参数**:
- `format`: `json` | `csv` | `excel` | `pdf` (默认: pdf)
- `language`: `zh-CN` | `en-US` (默认: zh-CN)

**响应** (PDF格式):
```
Content-Type: application/pdf
Content-Disposition: attachment; filename="AAPL_analysis_report.pdf"
```

### ⚙️ 配置管理

#### 获取系统配置
```http
GET /api/v1/config/system
```

**响应**:
```json
{
  "success": true,
  "data": {
    "version": "1.0.0",
    "supported_markets": [
      {
        "code": "us",
        "name": "美股",
        "data_sources": ["finnhub", "yahoo"],
        "currency": "USD"
      },
      {
        "code": "china",
        "name": "A股",
        "data_sources": ["tushare", "akshare"],
        "currency": "CNY"
      },
      {
        "code": "hk",
        "name": "港股",
        "data_sources": ["akshare", "yahoo"],
        "currency": "HKD"
      }
    ],
    "llm_providers": [
      {
        "code": "dashscope",
        "name": "阿里百炼",
        "models": ["qwen-turbo", "qwen-plus", "qwen-max"],
        "pricing": "CNY"
      },
      {
        "code": "openai",
        "name": "OpenAI",
        "models": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
        "pricing": "USD"
      }
    ],
    "features": {
      "real_time_analysis": true,
      "batch_analysis": true,
      "report_export": true,
      "user_management": true,
      "api_rate_limiting": true
    }
  }
}
```

### 🔍 健康检查

#### 系统健康状态
```http
GET /api/v1/health
```

**响应**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0",
  "uptime": 86400,
  "services": {
    "database": "healthy",
    "cache": "healthy",
    "llm_service": "healthy",
    "data_sources": {
      "finnhub": "healthy",
      "tushare": "degraded",
      "yahoo": "healthy"
    }
  },
  "metrics": {
    "requests_per_minute": 45,
    "average_response_time_ms": 850,
    "error_rate": 0.02,
    "active_users": 156
  }
}
```

## 错误处理

### HTTP状态码

- `200 OK`: 请求成功
- `201 Created`: 资源创建成功
- `400 Bad Request`: 请求参数错误
- `401 Unauthorized`: 认证失败
- `403 Forbidden`: 权限不足
- `404 Not Found`: 资源不存在
- `429 Too Many Requests`: 请求频率超限
- `500 Internal Server Error`: 服务器内部错误

### 错误响应格式

```json
{
  "success": false,
  "error": {
    "code": "INVALID_SYMBOL",
    "message": "股票代码格式无效",
    "details": {
      "symbol": "INVALID",
      "expected_format": "字母或数字组合，1-10个字符"
    },
    "request_id": "req_123456",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

### 常见错误代码

| 错误代码 | HTTP状态码 | 描述 | 解决方案 |
|-----------|------------|------|----------|
| `INVALID_API_KEY` | 401 | API密钥无效 | 检查API密钥格式和有效性 |
| `INSUFFICIENT_PERMISSIONS` | 403 | 权限不足 | 联系管理员升级权限 |
| `QUOTA_EXCEEDED` | 429 | 配额超限 | 等待配额重置或升级套餐 |
| `SYMBOL_NOT_FOUND` | 404 | 股票代码不存在 | 检查股票代码是否正确 |
| `INVALID_DATE_FORMAT` | 400 | 日期格式错误 | 使用YYYY-MM-DD格式 |
| `ANALYSIS_IN_PROGRESS` | 409 | 分析正在进行中 | 等待当前分析完成 |
| `RATE_LIMITED` | 429 | 请求频率限制 | 降低请求频率 |

## 限流规则

### API调用频率限制

| 端点 | 免费用户 | 专业用户 | 企业用户 |
|--------|----------|----------|----------|
| 分析启动 | 10次/小时 | 50次/小时 | 200次/小时 |
| 状态查询 | 60次/分钟 | 300次/分钟 | 1000次/分钟 |
| 数据查询 | 100次/分钟 | 500次/分钟 | 2000次/分钟 |
| 报告导出 | 20次/小时 | 100次/小时 | 500次/小时 |

### 响应头信息

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642230400
X-Request-ID: req_123456
X-Response-Time: 850
```

## SDK和代码示例

### Python SDK

```python
from tradingagents import TradingAgentsClient

# 初始化客户端
client = TradingAgentsClient(
    api_key="YOUR_API_KEY",
    base_url="http://localhost:8501/api/v1"
)

# 启动分析
analysis = client.analysis.start(
    symbol="AAPL",
    analysts=["market_analyst", "fundamentals_analyst"],
    research_depth=3
)

# 等待完成
analysis.wait_for_completion(timeout=300)

# 获取结果
results = analysis.get_results()
print(f"推荐: {results.recommendation.action}")
print(f"置信度: {results.recommendation.confidence}%")
```

### JavaScript SDK

```javascript
import { TradingAgentsClient } from '@tradingagents/api-client';

const client = new TradingAgentsClient({
    apiKey: 'YOUR_API_KEY',
    baseUrl: 'http://localhost:8501/api/v1'
});

// 异步分析
const analysis = await client.analysis.start({
    symbol: 'AAPL',
    analysts: ['market_analyst', 'fundamentals_analyst'],
    researchDepth: 3
});

// 监听进度
analysis.on('progress', (data) => {
    console.log(`进度: ${data.progress}%`);
    console.log(`当前步骤: ${data.current_step}`);
});

// 获取结果
const results = await analysis.getResults();
console.log('分析结果:', results);
```

### cURL 示例

```bash
# 健康检查
curl -X GET "http://localhost:8501/api/v1/health" \
     -H "Authorization: Bearer YOUR_API_KEY"

# 启动分析
curl -X POST "http://localhost:8501/api/v1/analysis/start" \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "symbol": "AAPL",
       "analysts": ["market_analyst", "fundamentals_analyst"],
       "research_depth": 3
     }'

# 查询状态
curl -X GET "http://localhost:8501/api/v1/analysis/analysis_123/status" \
     -H "Authorization: Bearer YOUR_API_KEY"

# 导出PDF报告
curl -X GET "http://localhost:8501/api/v1/reports/analysis_123/export?format=pdf&language=zh-CN" \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -o "AAPL_analysis_report.pdf"
```

## WebSocket API

### 实时分析进度

```javascript
const ws = new WebSocket('ws://localhost:8501/api/v1/ws/analysis/analysis_123');

ws.onopen = () => {
    console.log('WebSocket连接已建立');
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);

    switch(data.type) {
        case 'progress':
            console.log(`进度: ${data.progress}%`);
            console.log(`当前步骤: ${data.step}`);
            break;

        case 'completed':
            console.log('分析完成');
            console.log('结果:', data.results);
            break;

        case 'error':
            console.error('分析错误:', data.error);
            break;
    }
};
```

### 实时市场数据

```javascript
const ws = new WebSocket('ws://localhost:8501/api/v1/ws/market');

// 订阅股票价格
ws.send(JSON.stringify({
    action: 'subscribe',
    symbol: 'AAPL',
    type: 'price'
}));

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'price_update') {
        console.log(`${data.symbol}: $${data.price} (${data.change_percent}%)`);
    }
};
```

## 部署和配置

### 环境变量

```bash
# API配置
TRADINGAGENTS_API_KEY=your_api_key_here
TRADINGAGENTS_BASE_URL=http://localhost:8501/api/v1

# 数据源配置
DASHSCOPE_API_KEY=your_dashscope_key
FINNHUB_API_KEY=your_finnhub_key
TUSHARE_TOKEN=your_tushare_token

# 缓存配置
REDIS_URL=redis://localhost:6379
MONGODB_URL=mongodb://localhost:27017/tradingagents

# 安全配置
JWT_SECRET=your_jwt_secret_here
CORS_ORIGINS=http://localhost:3000,http://localhost:8501
```

### Docker 部署

```yaml
# docker-compose.api.yml
version: '3.8'

services:
  tradingagents-api:
    build: .
    ports:
      - "8501:8501"
    environment:
      - TRADINGAGENTS_API_KEY=${TRADINGAGENTS_API_KEY}
      - DASHSCOPE_API_KEY=${DASHSCOPE_API_KEY}
      - FINNHUB_API_KEY=${FINNHUB_API_KEY}
      - MONGODB_URL=mongodb://mongodb:27017/tradingagents
      - REDIS_URL=redis://redis:6379
    depends_on:
      - mongodb
      - redis
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data

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

### 启动服务

```bash
# 使用Docker Compose
docker-compose -f docker-compose.api.yml up -d

# 检查服务状态
docker-compose -f docker-compose.api.yml ps

# 查看日志
docker-compose -f docker-compose.api.yml logs -f tradingagents-api
```

## 更新日志

### v1.0.0 (2025-01-25)
- ✅ 完整重构API文档，基于新的模块化架构
- ✅ 添加WebSocket实时通信接口
- ✅ 完善错误处理和限流机制
- ✅ 提供多语言SDK和代码示例
- ✅ 更新部署配置和安全最佳实践

### 计划更新

- **v1.1.0**: 添加批量分析和订阅功能
- **v1.2.0**: 添加机器学习预测API
- **v1.3.0**: 添加移动端优化API

---

更多详细信息请参考：[TradingAgents-CN GitHub](https://github.com/hsliuping/TradingAgents-CN)