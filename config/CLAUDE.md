[根目录](../../CLAUDE.md) > **config**

# 配置管理模块

## 模块职责

Config模块负责TradingAgents-CN系统的配置管理，提供统一的配置接口和管理工具。主要功能包括：

- **系统配置**: 全局参数和环境变量管理
- **模型配置**: LLM模型参数和提供商设置
- **数据库配置**: MongoDB和Redis连接配置
- **API配置**: 外部服务API密钥和参数
- **用户配置**: Web界面用户权限和设置

## 入口与使用

### 配置文件结构
```
config/
├── settings.json          # 主配置文件
├── models.json           # AI模型配置
├── pricing.json          # 模型定价信息
├── usage.json            # 使用统计配置
├── logging.toml          # 日志配置
├── logging_docker.toml   # Docker日志配置
└── README.md             # 配置说明
```

### 使用方式
```python
# 读取配置
import json
with open('config/settings.json', 'r') as f:
    settings = json.load(f)

# 使用配置
default_provider = settings['default_provider']
data_dir = settings['data_dir']

# 通过配置管理器使用
from tradingagents.config import config_manager
api_key = config_manager.get_api_key('dashscope')
```

## 核心配置文件

### 1. 主配置文件 (`settings.json`)

#### 配置项说明
```json
{
  "default_provider": "dashscope",           // 默认LLM提供商
  "default_model": "qwen-turbo",             // 默认模型
  "enable_cost_tracking": true,              // 启用成本跟踪
  "cost_alert_threshold": 100.0,             // 成本警告阈值(元)
  "currency_preference": "CNY",              // 货币偏好
  "auto_save_usage": true,                   // 自动保存使用记录
  "max_usage_records": 10000,                // 最大使用记录数
  "data_dir": "/Users/berton/Documents/TradingAgents/data",  // 数据目录
  "cache_dir": "/Users/berton/Documents/TradingAgents/data/cache", // 缓存目录
  "results_dir": "./results",                // 结果目录
  "auto_create_dirs": true,                  // 自动创建目录
  "openai_enabled": false,                   // OpenAI启用状态
  "log_level": "DEBUG"                       // 日志级别
}
```

#### 数据源配置
```json
{
  "finnhub_api_key": "your_finnhub_api_key_here",
  "reddit_client_id": "your_reddit_client_id",
  "reddit_client_secret": "your_reddit_client_secret",
  "reddit_user_agent": "TradingAgents-CN/1.0"
}
```

### 2. 模型配置文件 (`models.json`)

#### 模型配置结构
```json
[
  {
    "provider": "dashscope",                 // 提供商
    "model_name": "qwen-turbo",             // 模型名称
    "api_key": "",                          // API密钥(从环境变量读取)
    "base_url": null,                       // 自定义端点
    "max_tokens": 4000,                     // 最大令牌数
    "temperature": 0.7,                     // 温度参数
    "enabled": true                         // 是否启用
  },
  {
    "provider": "deepseek",
    "model_name": "deepseek-chat",
    "api_key": "",
    "base_url": null,
    "max_tokens": 8000,
    "temperature": 0.7,
    "enabled": false
  }
]
```

#### 支持的提供商
- **dashscope**: 阿里百炼 (通义千问)
- **deepseek**: DeepSeek (深度求索)
- **openai**: OpenAI (GPT系列)
- **google**: Google AI (Gemini系列)

### 3. 定价配置文件 (`pricing.json`)

#### 价格信息
```json
{
  "models": {
    "qwen-turbo": {
      "input_price": 0.002,                 // 输入价格(元/千tokens)
      "output_price": 0.006,                // 输出价格
      "currency": "CNY",
      "provider": "dashscope"
    },
    "qwen-plus": {
      "input_price": 0.004,
      "output_price": 0.012,
      "currency": "CNY",
      "provider": "dashscope"
    },
    "deepseek-chat": {
      "input_price": 0.001,
      "output_price": 0.002,
      "currency": "CNY",
      "provider": "deepseek"
    }
  },
  "exchange_rates": {                       // 汇率信息
    "USD_TO_CNY": 7.2
  }
}
```

### 4. 使用统计配置 (`usage.json`)

#### 统计配置
```json
{
  "tracking_enabled": true,                 // 启用使用跟踪
  "save_interval": 3600,                    // 保存间隔(秒)
  "max_records": 10000,                     // 最大记录数
  "retention_days": 30,                     // 保留天数
  "categories": [                           // 统计类别
    "api_calls",
    "token_usage",
    "cost_tracking",
    "analysis_requests"
  ]
}
```

### 5. 日志配置文件 (`logging.toml`)

#### 日志配置
```toml
[formatters]
standard = { format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s" }
detailed = { format = "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s" }

[handlers]
console = { class = "logging.StreamHandler", level = "INFO", formatter = "standard" }
file = {
    class = "logging.handlers.RotatingFileHandler",
    level = "DEBUG",
    formatter = "detailed",
    filename = "logs/tradingagents.log",
    maxBytes = 104857600,  # 100MB
    backupCount = 5
}

[loggers]
tradingagents = { level = "DEBUG", handlers = ["console", "file"] }
web = { level = "INFO", handlers = ["console", "file"] }

[root]
level = "INFO"
handlers = ["console"]
```

## 环境变量配置

### .env文件配置模板
```bash
# ===========================================
# AI模型API配置
# ===========================================
# 阿里百炼 (推荐中文用户使用)
DASHSCOPE_API_KEY=sk-your-dashscope-key-here

# DeepSeek (高性价比)
DEEPSEEK_API_KEY=sk-your-deepseek-key-here

# Google AI
GOOGLE_API_KEY=your-google-api-key-here

# OpenAI (需要科学上网)
OPENAI_API_KEY=sk-your-openai-key-here

# ===========================================
# 数据源API配置
# ===========================================
# 金融数据源 (必需)
FINNHUB_API_KEY=your-finnhub-key-here

# A股专业数据源 (推荐)
TUSHARE_TOKEN=your-tushare-token-here
TUSHARE_ENABLED=true

# ===========================================
# 数据库配置 (可选)
# ===========================================
# MongoDB配置
MONGODB_ENABLED=true
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DATABASE=trading_agents
MONGODB_USERNAME=admin
MONGODB_PASSWORD=your-password

# Redis配置
REDIS_ENABLED=true
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your-password
REDIS_DB=0

# ===========================================
# 应用配置
# ===========================================
# 缓存类型
CACHE_TYPE=redis

# 日志级别
LOG_LEVEL=INFO

# 开发模式
DEBUG_MODE=false

# 功能开关
ONLINE_TOOLS_ENABLED=true
ONLINE_NEWS_ENABLED=true
REALTIME_DATA_ENABLED=false
MEMORY_ENABLED=true

# ===========================================
# Web应用配置
# ===========================================
# Streamlit配置
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_PORT=8501

# 安全配置
SECRET_KEY=your-secret-key-for-session-management
SESSION_TIMEOUT=3600

# ===========================================
# Docker部署配置 (Docker环境使用)
# ===========================================
DOCKER_CONTAINER=false
DISPLAY=:99

# 数据库连接 (Docker环境)
TRADINGAGENTS_MONGODB_URL=mongodb://admin:tradingagents123@mongodb:27017/tradingagents?authSource=admin
TRADINGAGENTS_REDIS_URL=redis://:tradingagents123@redis:6379
```

## 配置管理工具

### Python配置管理器
```python
# tradingagents/config/config_manager.py
class ConfigManager:
    """统一配置管理器"""

    def __init__(self):
        self.settings = self._load_settings()
        self.models = self._load_models()
        self.pricing = self._load_pricing()

    def get_api_key(self, provider: str) -> str:
        """获取API密钥"""
        env_key = f"{provider.upper()}_API_KEY"
        return os.getenv(env_key, "")

    def get_model_config(self, provider: str, model: str) -> dict:
        """获取模型配置"""
        for model_config in self.models:
            if (model_config['provider'] == provider and
                model_config['model_name'] == model):
                return model_config
        return None

    def update_setting(self, key: str, value: Any):
        """更新配置项"""
        self.settings[key] = value
        self._save_settings()
```

### Web配置界面
```python
# web/modules/config_management.py
def render_config_management():
    """渲染配置管理界面"""

    st.header("⚙️ 配置管理")

    # API配置
    with st.expander("🔑 API密钥配置", expanded=True):
        render_api_config()

    # 模型配置
    with st.expander("🤖 AI模型配置"):
        render_model_config()

    # 数据库配置
    with st.expander("🗄️ 数据库配置"):
        render_database_config()

    # 系统配置
    with st.expander("⚙️ 系统配置"):
        render_system_config()
```

## 数据库配置

### MongoDB配置
```python
# tradingagents/config/database_config.py
MONGODB_CONFIG = {
    'host': os.getenv('MONGODB_HOST', 'localhost'),
    'port': int(os.getenv('MONGODB_PORT', 27017)),
    'database': os.getenv('MONGODB_DATABASE', 'trading_agents'),
    'username': os.getenv('MONGODB_USERNAME', 'admin'),
    'password': os.getenv('MONGODB_PASSWORD', ''),
    'auth_source': os.getenv('MONGODB_AUTH_SOURCE', 'admin'),
    'connection_timeout': 5000,
    'socket_timeout': 30000,
    'max_pool_size': 50,
    'min_pool_size': 5,
}
```

### Redis配置
```python
REDIS_CONFIG = {
    'host': os.getenv('REDIS_HOST', 'localhost'),
    'port': int(os.getenv('REDIS_PORT', 6379)),
    'password': os.getenv('REDIS_PASSWORD', ''),
    'db': int(os.getenv('REDIS_DB', 0)),
    'decode_responses': True,
    'socket_timeout': 5,
    'socket_connect_timeout': 5,
    'max_connections': 20,
    'connection_pool_kwargs': {
        'retry_on_timeout': True,
        'health_check_interval': 30
    }
}
```

## 智能配置管理

### 配置优先级
1. **环境变量**: 最高优先级，适用于Docker和部署环境
2. **配置文件**: 中等优先级，适用于本地开发
3. **默认值**: 最低优先级，提供合理的默认配置

### 配置验证
```python
def validate_config():
    """验证配置完整性"""

    required_configs = [
        ('DASHSCOPE_API_KEY', 'DashScope API密钥'),
        ('FINNHUB_API_KEY', 'FinnHub API密钥'),
    ]

    missing_configs = []
    for env_key, description in required_configs:
        if not os.getenv(env_key):
            missing_configs.append(description)

    if missing_configs:
        raise ConfigError(f"缺少必需配置: {', '.join(missing_configs)}")
```

### 配置热更新
```python
def reload_config():
    """重新加载配置"""

    # 重新加载配置文件
    config_manager.reload()

    # 更新日志配置
    logging_config.reload()

    # 通知相关模块
    notify_config_change()
```

## 日志配置

### 日志级别说明
- **DEBUG**: 详细调试信息，开发环境使用
- **INFO**: 一般信息，生产环境推荐
- **WARNING**: 警告信息，需要关注
- **ERROR**: 错误信息，需要处理
- **CRITICAL**: 严重错误，系统级问题

### 日志文件配置
```toml
# logging_docker.toml - Docker环境日志配置
[handlers.file]
filename = "/app/logs/tradingagents.log"
maxBytes = 104857600  # 100MB
backupCount = 5

# 日志轮转
[handlers.file_rotating]
class = "logging.handlers.RotatingFileHandler"
when = "midnight"
interval = 1
backupCount = 30
```

## 成本控制配置

### 使用量跟踪
```python
# config/usage_tracking.py
class UsageTracker:
    """使用量跟踪器"""

    def track_api_call(self, provider: str, model: str,
                      input_tokens: int, output_tokens: int):
        """跟踪API调用"""

        cost = self.calculate_cost(provider, model,
                                 input_tokens, output_tokens)

        # 记录使用统计
        usage_record = {
            'timestamp': datetime.now(),
            'provider': provider,
            'model': model,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'cost': cost
        }

        self.save_usage_record(usage_record)

        # 检查成本警告
        if self.total_cost > self.cost_alert_threshold:
            self.send_cost_alert()
```

### 成本优化建议
1. **模型选择**: 根据任务复杂度选择合适模型
2. **缓存策略**: 启用智能缓存减少重复调用
3. **批量处理**: 合并多个小请求减少API调用
4. **监控告警**: 设置成本阈值和告警机制

## 安全配置

### API密钥安全
```python
def secure_api_keys():
    """API密钥安全处理"""

    # 从环境变量读取，不硬编码
    api_keys = {
        'dashscope': os.getenv('DASHSCOPE_API_KEY'),
        'deepseek': os.getenv('DEEPSEEK_API_KEY'),
        'openai': os.getenv('OPENAI_API_KEY')
    }

    # 验证密钥格式
    for provider, key in api_keys.items():
        if key and not validate_api_key_format(provider, key):
            raise SecurityError(f"无效的{provider} API密钥格式")

    return api_keys
```

### 权限控制
```json
{
  "user_roles": {
    "admin": [
      "config_management",
      "user_management",
      "cache_management",
      "system_logs"
    ],
    "user": [
      "stock_analysis",
      "view_reports",
      "export_reports"
    ],
    "viewer": [
      "view_reports",
      "stock_analysis"
    ]
  }
}
```

## 配置最佳实践

### 开发环境配置
```bash
# .env.development
LOG_LEVEL=DEBUG
DEBUG_MODE=true
MONGODB_ENABLED=false
REDIS_ENABLED=false
CACHE_TYPE=file
```

### 生产环境配置
```bash
# .env.production
LOG_LEVEL=INFO
DEBUG_MODE=false
MONGODB_ENABLED=true
REDIS_ENABLED=true
CACHE_TYPE=redis
```

### Docker环境配置
```bash
# .env.docker
DOCKER_CONTAINER=true
MONGODB_HOST=mongodb
REDIS_HOST=redis
TRADINGAGENTS_LOG_LEVEL=INFO
```

## 配置故障排除

### 常见配置问题

#### 1. API密钥无效
```bash
# 检查环境变量
echo $DASHSCOPE_API_KEY

# 验证密钥格式
python -c "
import re
key = 'your-key-here'
if re.match(r'^sk-[a-zA-Z0-9]+$', key):
    print('密钥格式正确')
else:
    print('密钥格式错误')
"
```

#### 2. 数据库连接失败
```python
# 测试数据库连接
from tradingagents.config.database_manager import DatabaseManager

try:
    db_manager = DatabaseManager()
    print(f"MongoDB: {db_manager.mongodb_available}")
    print(f"Redis: {db_manager.redis_available}")
except Exception as e:
    print(f"数据库连接失败: {e}")
```

#### 3. 配置文件格式错误
```bash
# 验证JSON格式
python -c "
import json
with open('config/settings.json') as f:
    config = json.load(f)
    print('配置文件格式正确')
"
```

### 配置调试工具
```python
# scripts/check_config.py
def check_all_configs():
    """检查所有配置"""

    print("🔍 配置检查报告")
    print("=" * 50)

    # 检查必需的环境变量
    check_required_env_vars()

    # 检查配置文件
    check_config_files()

    # 检查数据库连接
    check_database_connections()

    # 检查API连接
    check_api_connections()

    print("✅ 配置检查完成")
```

## 相关文件清单

### 配置文件 (核心)
- `settings.json` - 主配置文件
- `models.json` - AI模型配置
- `pricing.json` - 定价信息
- `usage.json` - 使用统计配置
- `logging.toml` - 日志配置

### 环境配置
- `.env.example` - 环境变量模板
- `.env` - 实际环境配置 (不提交版本控制)

### 配置管理代码
- `tradingagents/config/config_manager.py` - 配置管理器
- `tradingagents/config/database_manager.py` - 数据库管理
- `web/modules/config_management.py` - Web配置界面

### 配置工具
- `scripts/check_config.py` - 配置检查工具
- `scripts/setup/initialize_config.py` - 配置初始化

## 变更记录

- **2025-01-19**: 初始创建配置模块文档
- **2025-01-19**: 添加详细的环境变量配置说明
- **2025-01-19**: 完善安全和最佳实践指导

---

*此文档描述了配置管理模块的使用方法。配置时请确保API密钥和敏感信息的安全。*