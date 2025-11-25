# TradingAgents-CN 部署指南

## 🚀 部署概览

TradingAgents-CN 支持多种部署方式，从本地开发环境到生产级云部署，满足不同规模和需求。

## 🏗️ 部署架构

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                        用户界面层                                   │
│  ┌─────────────────┬─────────────────────────────────┬───────────────────┐ │
│  │ Streamlit   │     Vue.js         │    Nginx       │
│  │ (管理界面)    │    (用户界面)      │   (反向代理)    │
│  └─────────────┴─────────────────────────────────┴───────────────────┘ │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                         API 网关层                                   │
│  ┌─────────────┬─────────────────────────────────┬───────────────────┐ │
│  │  FastAPI    │     REST APIs      │   Authentication  │
│  └─────────────┴─────────────────────────────────┴───────────────────┘ │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                         业务逻辑层                                   │
│  ┌─────────────┬─────────────────────────────────┬───────────────────┐ │
│  │Multi-Agent │  Analysis Engine │  Background Tasks │
│  └─────────────┴─────────────────────────────────┴───────────────────┘ │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                         数据存储层                                   │
│  ┌─────────────┬─────────────────────────────────┬───────────────────┐ │
│  │  MongoDB    │     Redis         │   File System   │
│  │  (主数据库)  │   (缓存层)       │   (本地存储)   │
│  └─────────────┴─────────────────────────────────┴───────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

## 🐳 部署环境

### 开发环境
**适用场景**: 本地开发、功能测试、小规模部署

**技术栈**:
- Python 3.10+
- Docker + Docker Compose
- Redis + MongoDB
- Nginx (可选)

**快速启动**:
```bash
# 1. 使用开发环境配置
docker-compose -f docker-compose.dev.yml up -d

# 2. 验证部署
curl -X GET "http://localhost:8501/api/v1/health"
```

### 测试环境
**适用场景**: 集成测试、性能测试、预发布验证

**技术栈**:
- 与开发环境相同
- 包含完整的测试数据
- 支持负载测试

**配置示例**:
```yaml
# docker-compose.test.yml
version: '3.8'

services:
  tradingagents-api:
    build: .
    environment:
      - TESTING=true
      - MOCK_EXTERNAL_APIS=true
    depends_on:
      - mongodb
      - redis
    volumes:
      - ./tests:/app/tests
      - ./config:/app/config

  mongodb:
    image: mongo:6.0
    volumes:
      - mongodb_data:/data/db
      - mongodb_logs:/logs

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
```

### 预发布环境
**适用场景**: 类生产环境、用户验收测试

**技术栈**:
- 与生产环境相同
- 使用模拟数据
- 完整监控和日志

**配置示例**:
```yaml
# docker-compose.staging.yml
version: '3.8'

services:
  tradingagents-api:
    build: .
    environment:
      - ENVIRONMENT=staging
      - MOCK_EXTERNAL_APIS=false
    depends_on:
      - mongodb
      - redis
    volumes:
      - ./logs:/app/logs
      - ./config:/app/config

  mongodb:
    image: mongo:6.0
    volumes:
      - mongodb_staging_data:/data/db
      - mongodb_logs:/logs

  redis:
    image: redis:7-alpine
    volumes:
      - redis_staging_data:/data
```

### 生产环境
**适用场景**: 生产部署、大规模用户访问

**技术栈**:
- 容器编排：Docker + Kubernetes/Orchestration
- 负载均衡：Nginx/Traefik
- 监控系统：Prometheus + Grafana
- 日志系统：ELK Stack

## 🐳 容器化部署

### Docker部署

#### 1. 基础配置
```bash
# 构建镜像
docker build -t tradingagents-cn .

# 运行容器
docker run -d \
  -p 8501:8501 \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/logs:/app/logs \
  tradingagents-cn:latest \
  --env-file .env
```

#### 2. Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  tradingagents-api:
    build: .
    ports:
      - "8501:8501"
    environment:
      - DASHSCOPE_API_KEY=${DASHSCOPE_API_KEY}
      - FINNHUB_API_KEY=${FINNHUB_API_KEY}
      - MONGODB_URL=${MONGODB_URL}
      - REDIS_URL=${REDIS_URL}
    depends_on:
      - mongodb
      - redis
    volumes:
      - ./logs:/app/logs
      - ./config:/app/config
      - mongodb_data:/data/db
      redis_data:/data

  mongodb:
    image: mongo:6.0
    volumes:
      - mongodb_data:/data/db
      - mongodb_logs:/logs
    environment:
      - MONGO_INITDB_ROOT_USERNAME=admin
      - MONGO_INITDB_ROOT_PASSWORD=admin123
      - MONGO_INITDB_DATABASE=tradingagents

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - tradingagents-api
```

#### 3. 环境变量配置
```bash
# .env
# 生产环境配置
ENVIRONMENT=production
DEBUG_MODE=false
LOG_LEVEL=INFO

# 数据库配置
MONGODB_ENABLED=true
MONGODB_URL=mongodb://admin:admin123@mongodb:27017/tradingagents?authSource=admin
REDIS_ENABLED=true
REDIS_URL=redis://:tradingants123@redis:6379/0

# API密钥
DASHSCOPE_API_KEY=sk-xxxxxxxxx
FINNHUB_API_KEY=xxxxxxxxx
DEEPSEEK_API_KEY=sk-xxxxxxxxx

# 安全配置
SECRET_KEY=your-super-secret-jwt-key
CORS_ORIGINS=http://localhost:8501
ALLOWED_HOSTS=*

# 性能配置
MAX_WORKERS=4
CACHE_TTL=3600
API_RATE_LIMIT=100
REQUEST_TIMEOUT=60
```

### Kubernetes部署

#### 1. 基础部署
```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: tradingagents
```

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tradingagents-api
  labels:
    app: tradingagents
spec:
  replicas: 3
  selector:
    matchLabels:
      app: tradingagents
  template:
    metadata:
      labels:
        app: tradingagents
    spec:
      containers:
      - name: tradingagents-api
        image: tradingagents-cn:latest
        ports:
          - containerPort: 8501
        env:
          - name: ENVIRONMENT
            value: "production"
          - name: MONGODB_URL
            valueFrom:
              secretKeyRef: mongodb-url
          - name: REDIS_URL
            valueFrom:
              secretKeyRef: redis-url
          - name: DASHSCOPE_API_KEY
            valueFrom:
              secretKeyRef: dashscope-api-key
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
        volumeMounts:
          - name: config-volume
            mountPath: /app/config
          - name: logs-volume
            mountPath: /app/logs
```

#### 2. 密存和持久化
```yaml
# k8s/persistent-volume.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mongodb-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mongodb-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

#### 3. 配置管理
```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: tradingagents-config
data:
  ENVIRONMENT: "production"
  LOG_LEVEL: "INFO"
  MAX_WORKERS: "4"
  API_RATE_LIMIT: "100"
```

#### 4. 密钥管理
```yaml
# k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: tradingagents-secrets
type: Opaque
data:
  DASHSCOPE_API_KEY: <base64-encoded-key>
  FINNHUB_API_KEY: <base64-encoded-key>
  MONGODB_URL: mongodb://admin:password@mongodb:27017/tradingagents
  REDIS_URL: redis://:password@redis:6379/0
  SECRET_KEY: <base64-encoded-jwt-key>
```

### 5. 服务和Ingress
```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: tradingagents-api-service
spec:
  selector:
    app: tradingagents
  ports:
    - port: 8501
      targetPort: 8501
      nodePort: 30001
  type: LoadBalancer
  type: ClusterIP
  sessionAffinity: ClientIP
```

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1beta1
kind: Ingress
metadata:
  name: tradingagents-ingress
  annotations:
    kubernetes.io/ingress.class: "nginx"
spec:
  rules:
    - host: api.tradingagents.com
    http:
      paths:
        - path: /
          backend:
            service:
              name: tradingagents-api-service
              port:
                number: 8501
  tls:
                - termination: edge
  tls:
                  - hosts:
                    - api.tradingagents.com
```

### Helm Charts
```bash
# 创建 Helm Chart
helm create tradingagents-chart \
  --dependency-update tradingagents-cn \
  --version 0.1.0 \
  --app-version 1.0.0

# Chart 结构
tradingagents-chart/
├── Chart.yaml          # Chart 元数据
├── values.yaml           # 默认配置
├── templates/
│   ├── deployment.yaml    # K8s 部署模板
│   ├── service.yaml       # K8s 服务模板
│   ├── ingress.yaml        # K8s Ingress 模板
│   └── configmap.yaml    # 配置映射模板
└── templates/tests/     # 测试模板
```

## ☁️ 云平台部署

### 阿里云
```bash
# 1. 创建ECS实例
ecs-cli configure region us-west-2 \
  --instance-type t3.medium \
  --image-id ami-123456789 \
  --key-pair TradingAgentsKeyPair \
  --iam-instance-profile arn:aws:iam::123456789:instance-profile/tradingagents \
  --security-group tradingagents-admin \
  --tag Environment=Production

# 2. 部署服务
ecs-cli up --cluster tradingagents-cluster \
  --service tradingagents-service \
  --task-definition tradingagents-task

# 3. 配置负载均衡器
ecs-cli register-load-balancer \
  --name tradingagents-elb \
  --subnets tradingagents-subnet \
  --security-group tradingagents-security \
  --listener protocol TCP:80 \
  --default-actions target-group-arn:arn:aws:elasticloadbalancing:target-groups/tradingagents
```

### 腾里云
```bash
# 1. 创建资源组
az group create \
  --name TradingAgents-RG \
  --location eastus

# 2. 创建应用服务计划
az appservice plan create \
  --name tradingagents-app \
  --resource-group TradingAgents-RG \
  --sku B1 \
  --instance-count 3

# 3. 部署应用
az appservice up \
  --resource-group TradingAgents-RG \
  --name tradingagents-app \
  --plan tradingagents-app-plan

# 4. 配置应用网关
az network gateway create \
  --resource-group TradingAgents-RG \
  --name tradingagents-gateway \
  --location eastus \
  --public-ip-address true \
  --sku Standard_v2
```

### 腷里云 (腾讯云)
```bash
# 1. 登录腾讯云
ccloud login

# 2. 创建集群
ccloud ccs create cluster-id=tradingagents-cluster \
  --region=ap-chengdu \
  --zone=ap-chengdu-1 \
  --node-type=2RAM.4G \
  --count=3

# 3. 部署应用
ccloud tccli create service \
  --cluster-id tradingagents-cluster \
  --service-name tradingagents \
  --image tradingagents-cn:latest \
  --replicas=3
  --env-file tcloud.env

# 4. 配置负载均衡
ccloud clb create lb \
  --name tradingagents-lb \
  --type=PUBLIC \
  --region=ap-chengdu \
  --security-group=tradingagents-security \
  --domain=api.tradingagents.com
```

### 华为云
```bash
# 1. 登录华为云
hcloud login

# 2. 创建集群
hcloud cci create cluster \
  --region cn-north-4 \
  --node-type general-purpose \
  --node-count 3 \
  --name tradingagents-cluster

# 3. 部署服务
hcloud cci create service \
  --cluster tradingagents-cluster \
  --service-name tradingagents-api \
  --image tradingagents-cn:latest \
  --replicas 3
  --env-file hcloud.env
```

## 🔧 环境配置

### 环境变量配置
```bash
# 生产环境 (.env)
ENVIRONMENT=production
DEBUG_MODE=false
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8501
MAX_WORKERS=8
CACHE_TTL=7200

# 数据库配置
MONGODB_URL=mongodb://user:password@mongodb:27017/tradingagents
MONGODB_DATABASE=tradingagents
REDIS_URL=redis://:password@redis:6379/0
DATABASE_POOL_SIZE=20
CACHE_POOL_MAX_SIZE=50

# 安全配置
SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION=86400
CORS_ORIGINS=https://api.tradingagents.com
ALLOWED_HOSTS=api.tradingagents.com

# 监控配置
PROMETHEUS_ENDPOINT=http://prometheus:9090
GRAFANA_ENDPOINT=http://grafana:3000
Sentry_DSN=your-sentry-dsn
```

### Docker Compose 配置

#### 开发环境 (docker-compose.dev.yml)
```yaml
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
      - RELOAD=true
    volumes:
      - .:/app
      - ./logs:/app/logs
      - ./config:/app/config
    depends_on:
      - mongodb
      - redis

  mongodb:
    image: mongo:6.0
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
      - mongodb_logs:/logs

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  dev-tools:
    image: tradingagents-cn:latest
    command: pytest
    volumes:
      - .:/app
    environment:
      - TESTING=true
```

#### 生产环境 (docker-compose.prod.yml)
```yaml
version: '3.8'

services:
  tradingagents-api:
    image: tradingagents-cn:latest
    restart: unless-stopped
    ports:
      - "8501:8501"
    environment:
      - ENVIRONMENT=production
      - DEBUG_MODE=false
      - RELOAD=false
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1000m'
          memory: '2Gi'
    volumes:
      - ./logs:/app/logs
      - ./config:/app/config
      - mongodb_data:/data/db
    depends_on:
      - mongodb
      - redis
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/api/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - tradingagents-api
    restart: unless-stopped
```

#### 高可用环境 (docker-compose.ha.yml)
```yaml
version: '3.8'

services:
  tradingagents-api-1:
    image: tradingagents-cn:latest
    environment:
      - ENVIRONMENT=production
      - REDIS_URL=redis://redis-1:6379/1
    deploy:
      replicas: 2
    depends_on:
      - redis-1

  tradingagents-api-2:
    image: tradingagents-cn:latest
    environment:
      - ENVIRONMENT=production
      - REDIS_URL=redis://redis-2:6379/1
    deploy:
      replicas: 2
    depends_on:
      - redis-2

  redis-1:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis-1_data:/data

  redis-2:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis-2_data:/data

  nginx-ha:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx-ha.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - tradingagents-api-1
      - tradingagents-api-2
```

## 🚦 监控和日志

### 应用监控
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'tradingagents'
    static_configs:
      - targets: ['localhost:8501/api/v1/metrics']
    metrics_path: '/api/v1/metrics'
    params:
      format: 'prometheus'
```

### 日志聚合
```yaml
# filebeat.yml
filebeat.inputs:
  - type: log
  paths:
    - /app/logs/*.log

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
  index: "tradingagents-logs"

logging:
  level: info
  codecs: plain
  filebeat:
    name: tradingagents-logs
    keep_fields: ["timestamp", "level", "message"]
```

## 🔒 安全配置

### SSL/TLS配置

### 证书管理
```bash
# 生成自签名证书
openssl req -x509 -newkey rsa:2048 \
  -newkey ec:256 \
  -nodes \
  -days 365 \
  -out tradingagents-cert.pem \
  -keyout tradingagents-key.pem \
  -subj "/C=CN/O=TradingAgents" \
  -reqext SAN=api.tradingagents.com

# 配置Nginx SSL
server {
    listen 443 ssl http2;
    ssl_certificate /etc/ssl/tradingagents-cert.pem;
    ssl_certificate_key /etc/ssl/tradingagents-key.pem;
    ssl_session_timeout 1d;

    location / {
        /api/ {
            proxy_pass http://localhost:8501;
            proxy_set_header Host $http_host;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

### 网络安全
```yaml
# docker-compose.security.yml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:443"
    volumes:
      - ./nginx/security.conf:/etc/nginx/conf.d:ro
      - ./ssl:/etc/ssl:/ro
    depends_on:
      - tradingagents-api

  tradingagents-api:
    build: .
    networks:
      - tradingagents-internal
    environment:
      - ENABLE_NETWORK_MODE=true
    deploy:
      replicas: 3
```
```

networks:
  tradingagents-internal:
    driver: bridge
    internal: true
    ipam:
      config:
        - subnet: 172.20.0.0/16
        ip_range: 172.20.0.2-172.20.0.254
```

### 访问控制
```yaml
# docker-compose.access-control.yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx/access-control.conf:/etc/nginx/conf.d:ro
    depends_on:
      - tradingagents-api

  redis:
    image: redis:7-alpine
    volumes:
      - ./redis/access-control:/data
      - ./redis/access-control.conf
    command: redis-server --appendonly yes --requirepass your-redis-password

  tradingagents-api:
    build: .
    networks:
      - tradingagents-internal
    environment:
      - ENABLE_ACCESS_CONTROL=true
      - ACCESS_TOKEN_HEADER=X-Access-Token
      - ENABLE_RATE_LIMITING=true
    depends_on:
      - redis
      - nginx
```

## 📊 备份和恢复

### 数据备份策略
```bash
# MongoDB备份
mongodump --uri mongodb://user:password@localhost:27017/tradingagents \
  --out /backup/mongodb/backup-$(date +%Y%m%d).tar.gz

# 增量备份
rsync -av /data/db/ /backup/incremental/$(date +%Y%m%d)/

# 应用备份
tar -czf /app/ backup/application-$(date +%Y%m%d).tar.gz \
  --exclude=node_modules \
  --exclude=.env \
  /app/ backup/

# 配置文件备份
tar -czf config/ backup/config-$(date +%Y%m%d).tar.gz \
  /docker-compose.yml
```

### 恢复策略
```bash
# 恢复数据库
mongorestore --uri mongodb://user:password@localhost:27017/tradingagents \
  --db tradingagents \
  --drop \
  --restore /backup/mongodb/backup-2024-01-15.tar.gz

# 恢复应用
tar -xzf /backup/application-2024-01-15.tar.gz

# 验证恢复
curl -X GET "http://localhost:8501/api/v1/health"
```

## 🚀 性能优化

### 应用性能优化
```yaml
# docker-compose.performance.yml
version: '3.8'

services:
  tradingagents-api:
    image: tradingagents-cn:latest
    environment:
      - PYTHONUNBUFFERED=1
      - WORKERS=4
      - MAX_REQUESTS=1000
      - REQUEST_TIMEOUT=60
    deploy:
      replicas: 4
      resources:
        limits:
          cpus: '2000m'
          memory: '4Gi'
        reservations:
          cpus: '1000m'
          memory: '2Gi'
    volumes:
      - ./logs:/app/logs
    depends_on:
      - mongodb
      - redis
```

### 数据库优化
```javascript
// MongoDB索引优化
db.analysis.createIndex({ "symbol": 1, "analysis_date": -1 }, { name: "idx_symbol_date", unique: true })
db.analysis.createIndex({ "symbol": 1, "created_at": -1 }, { name: "idx_created_at" })
db.analysis.createIndex({ "provider": 1, "model": 1 }, { name: "idx_provider_model" })

// Redis配置优化
maxmemory-policy allkeys-lru
maxmemory-samples 25
save 900 1 10 300
```

### 缓存优化
```python
# 智能缓存配置
CACHE_CONFIG = {
    'max_memory_size': 100 * 1024 * 1024,  # 100MB
    'strategy': 'adaptive',
    'ttl_patterns': {
        'stock_data': 3600,  # 1小时
        'analysis_results': 1800, # 30分钟
        'user_sessions': 7200,  # 2小时
    }
}

# 缓存预热
def warm_up_cache():
    # 预加载热点数据
    pass
```

## 🔧 故障排除

### 常见问题

#### 1. 数据库连接问题
```bash
# 检查MongoDB连接
docker exec -it tradingagents-mongodb mongo \
  --eval "db.adminCommand('ismaster')"

# 检查Redis连接
docker exec -it tradingagents-redis redis-cli \
  PING

# 检查网络连接
docker exec -it tradingagents-api \
  curl -X GET "http://localhost:8501/api/v1/health"
```

#### 2. 内存问题
```bash
# 检查容器内存使用
docker stats tradingagents-api

# 检查磁盘空间
df -h

# 清理未使用的容器
docker system prune -f
```

#### 3. 性能问题
```bash
# 检查CPU使用率
docker exec -it tradingagents-api top
top -c

# 检查响应时间
time curl -o /dev/null -s -w "%{http_code}\n" \
     -X GET "http://localhost:8501/api/v1/metrics" \
     -w "%{time_total}\n"

# 分析慢查询
docker exec -it tradingagents-api \
  python -m cProfile -o profiling.stats \
     -c "from tradingagents.api.main import app; app()"
```

#### 4. 应用崩溃问题
```bash
# 检查应用日志
docker logs tradingagents-api --tail 100

# 检查系统资源
docker exec -it tradingagents-api \
  free -h && df -h

# 重启应用服务
docker-compose restart tradingagents-api

# 检查依赖服务
docker-compose ps
```

#### 5. SSL证书问题
```bash
# 检查证书有效期
openssl x509 -in /etc/ssl/certs/api.crt -noout -dates

# 验证证书链
openssl verify -CAfile /etc/ssl/certs/ca.crt \
  /etc/ssl/certs/api.crt

# 测试HTTPS连接
curl -v https://api.tradingagents-cn.com/api/v1/health
```

#### 6. 权限和安全问题
```bash
# 检查文件权限
ls -la /app/keys/ /app/logs/

# 修复权限问题
docker exec -it tradingagents-api \
  chown -R app:app /app/keys/ /app/logs/

# 检查防火墙规则
ufw status
iptables -L
```

## 🚨 紧急响应流程

### 生产环境故障响应
```bash
#!/bin/bash
# scripts/emergency_response.sh

set -e

SEVERITY=${1:-medium}
COMPONENT=${2:-all}

echo "🚨 紧急响应流程启动 - 严重级别: $SEVERITY"

# 1. 快速评估
echo "📊 系统状态评估..."
docker-compose ps
curl -s http://localhost:8501/api/v1/health || echo "API服务异常"

# 2. 立即保护措施
if [ "$SEVERITY" = "critical" ]; then
    echo "🛡️ 执行关键保护措施..."

    # 切换到只读模式
    curl -X POST "http://localhost:8501/api/v1/admin/maintenance" \
         -H "Authorization: Bearer $ADMIN_TOKEN" \
         -d '{"mode": "readonly"}'

    # 保存当前状态
    docker-compose logs > emergency-logs-$(date +%Y%m%d-%H%M%S).log

    # 通知团队
    curl -X POST "https://hooks.slack.com/services/$SLACK_WEBHOOK" \
         -d '{"text": "🚨 TradingAgents-CN 紧急维护模式已启动"}'
fi

# 3. 组件特定响应
case $COMPONENT in
    "api")
        echo "🔧 API组件故障响应..."
        docker-compose restart tradingagents-api
        ;;
    "database")
        echo "💾 数据库组件故障响应..."
        docker-compose restart mongodb
        docker exec tradingagents_mongodb mongod --repair
        ;;
    "cache")
        echo "⚡ 缓存组件故障响应..."
        docker-compose restart redis
        docker exec tradingagents_redis redis-cli FLUSHALL
        ;;
    "all")
        echo "🔄 全系统重启..."
        docker-compose restart
        ;;
esac

# 4. 验证恢复
echo "🔍 验证系统恢复..."
sleep 30

for i in {1..5}; do
    HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8501/api/v1/health)
    if [ "$HEALTH_STATUS" = "200" ]; then
        echo "✅ 系统恢复成功"
        break
    else
        echo "⏳ 等待系统恢复... ($i/5)"
        sleep 30
    fi
done

# 5. 发送状态通知
if [ "$HEALTH_STATUS" = "200" ]; then
    curl -X POST "https://hooks.slack.com/services/$SLACK_WEBHOOK" \
         -d '{"text": "✅ TradingAgents-CN 系统已恢复正常"}'
else
    curl -X POST "https://hooks.slack.com/services/$SLACK_WEBHOOK" \
         -d '{"text": "❌ TradingAgents-CN 系统恢复失败，需要人工介入"}'
fi

echo "📋 紧急响应流程完成"
```

### 数据恢复流程
```bash
#!/bin/bash
# scripts/data_recovery.sh

BACKUP_DATE=${1:-$(date +%Y%m%d)}
RECOVERY_TYPE=${2:-full}

echo "🔄 开始数据恢复 - 备份日期: $BACKUP_DATE"

# 1. 停止相关服务
echo "⏸️ 停止服务..."
docker-compose stop tradingagents-api

# 2. 数据库恢复
if [ "$RECOVERY_TYPE" = "full" ] || [ "$RECOVERY_TYPE" = "database" ]; then
    echo "💾 恢复数据库..."
    docker-compose stop mongodb

    # 备份当前数据
    mv /var/lib/mongodb /var/lib/mongodb.backup.$(date +%Y%m%d-%H%M%S)

    # 恢复备份
    tar -xzf /backup/mongodb/backup-$BACKUP_DATE.tar.gz -C /

    docker-compose start mongodb
    sleep 30
fi

# 3. 缓存恢复
if [ "$RECOVERY_TYPE" = "full" ] || [ "$RECOVERY_TYPE" = "cache" ]; then
    echo "⚡ 恢复缓存..."
    docker-compose restart redis
fi

# 4. 应用配置恢复
if [ "$RECOVERY_TYPE" = "full" ]; then
    echo "⚙️ 恢复应用配置..."
    tar -xzf /backup/application/backup-$BACKUP_DATE.tar.gz -C /app/
fi

# 5. 验证恢复
echo "🔍 验证数据恢复..."
docker-compose start tradingagents-api
sleep 60

# 数据完整性检查
docker exec tradingagents-api python -c "
from tradingagents.database import DatabaseManager
db = DatabaseManager()
result = db.verify_data_integrity()
print(f'数据完整性检查: {\"通过\" if result else \"失败\"}')
"

# API功能测试
curl -X POST "http://localhost:8501/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"username": "test", "password": "test"}' \
     && echo "✅ API功能正常" || echo "❌ API功能异常"

echo "📋 数据恢复流程完成"
```

## 📊 容量规划

### 硬件资源规划

#### 小型部署（100-500用户）
```yaml
# docker-compose.small.yml
version: '3.8'

services:
  tradingagents-api:
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '1000m'
          memory: '2Gi'
        reservations:
          cpus: '500m'
          memory: '1Gi'

  mongodb:
    deploy:
      resources:
        limits:
          cpus: '500m'
          memory: '2Gi'
        reservations:
          cpus: '250m'
          memory: '1Gi'

  redis:
    deploy:
      resources:
        limits:
          cpus: '250m'
          memory: '1Gi'
        reservations:
          cpus: '100m'
          memory: '512Mi'

# 推荐配置
# CPU: 4核心
# 内存: 8GB
# 存储: 100GB SSD
# 网络: 100Mbps
```

#### 中型部署（500-2000用户）
```yaml
# docker-compose.medium.yml
version: '3.8'

services:
  tradingagents-api:
    deploy:
      replicas: 4
      resources:
        limits:
          cpus: '1500m'
          memory: '3Gi'
        reservations:
          cpus: '750m'
          memory: '1.5Gi'

  mongodb:
    deploy:
      resources:
        limits:
          cpus: '1000m'
          memory: '4Gi'
        reservations:
          cpus: '500m'
          memory: '2Gi'

  redis:
    deploy:
      resources:
        limits:
          cpus: '500m'
          memory: '2Gi'
        reservations:
          cpus: '250m'
          memory: '1Gi'

# 推荐配置
# CPU: 8核心
# 内存: 16GB
# 存储: 500GB SSD
# 网络: 1Gbps
```

#### 大型部署（2000+用户）
```yaml
# docker-compose.large.yml
version: '3.8'

services:
  tradingagents-api:
    deploy:
      replicas: 8
      resources:
        limits:
          cpus: '2000m'
          memory: '4Gi'
        reservations:
          cpus: '1000m'
          memory: '2Gi'

  mongodb:
    image: mongo:6.0
    command: mongod --replSet rs0 --shardsvr
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2000m'
          memory: '8Gi'
        reservations:
          cpus: '1000m'
          memory: '4Gi'

  redis:
    image: redis:7-alpine
    command: redis-server --cluster-enabled yes
    deploy:
      replicas: 6
      resources:
        limits:
          cpus: '1000m'
          memory: '4Gi'
        reservations:
          cpus: '500m'
          memory: '2Gi'

# 推荐配置
# CPU: 16核心
# 内存: 32GB
# 存储: 2TB SSD
# 网络: 10Gbps
```

### 扩展策略

#### 水平扩展
```bash
#!/bin/bash
# scripts/scale_horizontal.sh

INSTANCE_COUNT=${1:-2}

echo "📈 水平扩展到 $INSTANCE_COUNT 个实例"

# 1. 更新Docker Compose配置
sed -i "s/replicas: [0-9]*/replicas: $INSTANCE_COUNT/" docker-compose.yml

# 2. 重新部署
docker-compose up -d --scale tradingagents-api=$INSTANCE_COUNT

# 3. 更新负载均衡器
docker-compose restart nginx

# 4. 验证扩展
curl -X GET "http://localhost/api/v1/metrics" \
     && echo "✅ 水平扩展成功"
```

#### 垂直扩展
```bash
#!/bin/bash
# scripts/scale_vertical.sh

CPU_LIMITS=${1:-2000m}
MEMORY_LIMITS=${2:-4Gi}

echo "⬆️ 垂直扩展到 CPU:$CPU_LIMITS, 内存:$MEMORY_LIMITS"

# 1. 更新资源限制
sed -i "s/cpus: '[0-9]*m'/cpus: '$CPU_LIMITS'/" docker-compose.yml
sed -i "s/memory: '[0-9]*Gi'/memory: '$MEMORY_LIMITS'/" docker-compose.yml

# 2. 重新部署
docker-compose up -d

# 3. 验证扩展
docker stats tradingagents-api --no-stream
```

## 🔗 相关链接

- **项目主页**: [TradingAgents-CN GitHub](https://github.com/hsliuping/TradingAgents-CN)
- **API文档**: [API参考文档](../api/README.md)
- **开发指南**: [开发指南](DEVELOPMENT.md)
- **贡献指南**: [贡献指南](../CONTRIBUTING.md)
- **问题反馈**: [GitHub Issues](https://github.com/hsliuping/TradingAgents-CN/issues)

---

**更新日期**: 2025-01-25
**版本**: v1.0.0
**维护者**: TradingAgents-CN 开发团队

---

*本部署文档涵盖了从开发环境到生产环境的完整部署方案，包括性能优化、监控告警、故障排除和紧急响应流程。如有问题请提交Issue或PR进行修正。*
# 检查应用日志
docker logs tradingagents-api --tail 100

# 检查容器状态
docker ps -a tradingagents-api

# 重启应用
docker restart tradingagents-api

# 进入容器调试
docker exec -it tradingagents-api bash
```

## 📊 升级和回滚

### 版本管理
```bash
# 标记版本
git tag -a v1.0.0 -m "Release v1.0.0"

# 回滚到上一版本
git checkout v0.9.9

# 查看版本差异
git log --oneline --graph --decorate

# 创建回滚脚本
#!/bin/bash
git checkout main
git reset --hard v1.0.0
git push -f origin main --force
```

### 灰度部署
```bash
# 蓝度部署脚本
#!/bin/bash

# 1. 备份当前版本
git tag -a backup-v1.0.0

# 2. 部署新版本
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d

# 3. 验证部署
sleep 30
curl -f "http://your-domain.com/api/v1/health"

# 4. 回滚策略
# 如果部署失败，自动回滚
if [ $? -ne 0 ]; then
    echo "部署失败，开始回滚..."
    docker-compose -f docker-compose.prod.yml down
    docker load backup-v1.0.0
    docker-compose -f docker-compose.prod.yml up -d
fi
```

## 🔄 CI/CD 集成

### GitHub Actions 配置
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Setup environment
        run: |
          echo "Setting up production environment..."
          # 环境设置步骤

      - name: Deploy to production
        run: |
          echo "Deploying to production..."
          docker-compose -f docker-compose.prod.yml up -d
          sleep 60

      - name: Health check
        run: |
          echo "Checking deployment health..."
          timeout 300 bash -c "
            until curl -f http://your-domain.com/api/v1/health; do
              sleep 10
              curl -f http://your-domain.com/api/v1/health; exit 0; do
              break
            done"

      - name: Rollback on failure
        if: failure()
        run: |
          echo "Deployment failed, rolling back..."
          docker-compose -f docker-compose.prod.yml down
          # 回滚逻辑
```

### 多环境管理
```yaml
# .github/workflows/environments.yml
name: Environment Management

on:
  workflow_call:
    workflows: [deploy-staging, deploy-production]

jobs:
  deploy-staging:
    uses: ./.github/workflows/deploy.yml
    with:
      environment: staging
    strategy:
      matrix:
        environment: [staging-eu, staging-us, staging-asia]

  deploy-production:
    uses: ./.github/workflows/deploy.yml
    with:
      environment: [production-eu, production-us, production-asia]
```

## 📋 监控和告警

### 告警规则
```yaml
# .github/workflows/monitoring.yml
name: Application Monitoring

on:
  schedule:
    - cron: '*/5 * * *'  # 每5分钟

jobs:
  health-check:
    runs-on: ubuntu-latest
    steps:
      - name: Check all services
        run: |
          curl -f http://api.tradingagents.com/api/v1/health

  performance-check:
    runs-on: ubuntu-latest
    steps:
      - name: Check response time
        run: |
          curl -o /dev/null -s "%{http_code}\n" \
               -X GET "http://api.tradingagents.com/api/v1/health" \
               -w "%{time_total}\n" \
               || exit 1

  error-check:
    runs-on: ubuntu-latest
    steps:
      - name: Check error logs
        run: |
          docker logs tradingagents-api --since=5m --tail 50
```

### 通知渠道
```yaml
# .github/workflows/notifications.yml
name: Notifications

on:
  issues:
    types: [opened, closed]
  labels: [bug, critical]

jobs:
  slack-notification:
    runs-on: ubuntu-latest
    if: contains(github.event.issue.labels.*['critical'])
    steps:
      - name: Send Slack notification
        run: |
          curl -X POST -H 'Content-Type: application/json' \
               -d '{"text": "Critical issue: ${{ github.event.issue.title }}", "channel": "#alerts"}' \
               ${{ secrets.SLACK_WEBHOOK }}
```

  email-notification:
    runs-on: ubuntu-latest
    steps:
      - name: Send email notification
        run: |
          curl -X POST -H 'Content-Type: application/json' \
               -d '{"to": "team@company.com", "subject": "Issue: ${{ github.event.issue.title }}", "body": "URL: ${{ github.event.html_url }}"}' \
               ${{ secrets.EMAIL_SMTP }}
```
```

## 🔧 扩展和插件

### 添加新数据源
1. **创建数据源适配器**
   ```python
   # tradingagents/dataflows/new_provider.py
   class NewProviderAdapter(BaseAdapter):
       def fetch_stock_data(self, symbol):
           # 实现数据获取逻辑
           pass
   ```

2. **注册适配器**
   ```python
   from tradingagents.dataflows.interface import register_provider
   register_provider('new_provider', NewProviderAdapter)
   ```

3. **更新配置**
   ```json
   {
     "providers": {
       "new_provider": {
         "name": "新数据源",
         "description": "新数据源描述",
         "enabled": true
       }
     }
   }
   ```

### 添加新LLM提供商
1. **创建LLM适配器**
   ```python
   # tradingagents.llm_adapters/new_provider.py
   class NewProviderAdapter(BaseLLMAdapter):
       def __init__(self, model, api_key, base_url=None):
           super().__init__()
   ```

2. **更新模型配置**
   ```json
   {
     "models": {
       "new_provider": {
         "models": ["model-v1", "model-v2"],
         "default": "model-v1"
       }
     }
   }
   ```

### 添加新智能体
1. **创建智能体**
   ```python
   # tradingagents/agents/specialists/new_analyst.py
   class NewAnalyst(BaseAnalyst):
       def analyze(self, state):
           # 实现分析逻辑
           pass
   ```

2. **注册智能体**
   ```python
   from tradingagents.graph.setup import register_analyst
   register_analyst('new_analyst', NewAnalyst)
   ```

## 🎯 性能监控

### 关键指标
- **响应时间**: API端点的平均响应时间
- **吞吐量**: 每秒处理的请求数量
- **错误率**: 失败请求的百分比
- **内存使用**: 容器内存占用
- **CPU使用**: 容器CPU使用率
- **缓存命中率**: 缓存系统命中率

### 监控工具
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'tradingagents-api'
    metrics_path: '/api/v1/metrics'
    scrape_interval: 15s
    metrics_path: '/api/v1/metrics'

  - job_name: 'tradingagents-db'
    metrics_path: '/api/v1/db/metrics'
    scrape_interval: 30s
    static_configs:
      - targets: ['localhost:27017']
```

### 告警规则
```yaml
# prometheus/rules.yml
groups:
  - name: tradingagents-alerts
    rules:
    - alert: CriticalError
      expr: job:tradingagents-api:job_errors:errors:rate(5m) > 0
      for: 1m
      annotations:
        summary: "High error rate detected"
        description: "TradingAgents API error rate > 5/m"

  - name: tradingagents-availability
    rules:
      - alert: ServiceDown
      expr: up == 0
      for: 5m
      annotations:
        summary: "Service appears down"
        description: "TradingAgents service is down"
```

---

*最后更新：2025-01-25*
*文档版本：v1.0.0*
*责任维护：TradingAgents-CN 开发团队*