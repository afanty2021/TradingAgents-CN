# Web服务配置

<cite>
**本文档中引用的文件**
- [docker-compose.yml](file://docker-compose.yml)
- [Dockerfile](file://Dockerfile)
- [web/app.py](file://web/app.py)
- [web/run_web.py](file://web/run_web.py)
- [config/logging_docker.toml](file://config/logging_docker.toml)
- [tradingagents/config/env_utils.py](file://tradingagents/config/env_utils.py)
- [tradingagents/config/database_config.py](file://tradingagents/config/database_config.py)
- [scripts/docker/README.md](file://scripts/docker/README.md)
</cite>

## 目录
1. [概述](#概述)
2. [Docker镜像构建配置](#docker镜像构建配置)
3. [容器服务配置](#容器服务配置)
4. [代码卷挂载与热重载](#代码卷挂载与热重载)
5. [环境变量覆盖机制](#环境变量覆盖机制)
6. [健康检查与重启策略](#健康检查与重启策略)
7. [网络配置](#网络配置)
8. [日志与配置持久化](#日志与配置持久化)
9. [性能调优建议](#性能调优建议)
10. [常见部署问题排查](#常见部署问题排查)

## 概述

TradingAgents项目的Web服务基于Docker Compose进行容器化部署，提供了一个完整的股票分析平台。该配置包含了Web应用、数据库服务（MongoDB和Redis）以及管理界面，形成了一个自包含的微服务架构。

```mermaid
graph TB
subgraph "Docker网络"
Web[TradingAgents-web<br/>端口8501]
MongoDB[TradingAgents-mongodb<br/>端口27017]
Redis[TradingAgents-redis<br/>端口6379]
RedisCmd[TradingAgents-redis-commander<br/>端口8081]
MongoExpress[Mongo-Express<br/>端口8082]
end
subgraph "外部访问"
Browser[浏览器<br/>http://localhost:8501]
AdminUI[管理界面<br/>http://localhost:8081/8082]
end
Browser --> Web
AdminUI --> RedisCmd
AdminUI --> MongoExpress
Web --> MongoDB
Web --> Redis
RedisCmd --> Redis
MongoExpress --> MongoDB
```

**图表来源**
- [docker-compose.yml](file://docker-compose.yml#L1-L159)

## Docker镜像构建配置

### 构建上下文与基础镜像

项目使用官方Python 3.10 Slim Bookworm镜像作为基础，确保最小化体积和安全性：

```yaml
build: .
image: tradingagents-cn:latest
container_name: TradingAgents-web
```

### 多源依赖安装策略

Dockerfile实现了智能的依赖安装机制，通过多个镜像源轮询确保安装成功率：

```bash
# 多源轮询安装依赖
for src in \
    https://mirrors.aliyun.com/pypi/simple \
    https://pypi.tuna.tsinghua.edu.cn/simple \
    https://pypi.doubanio.com/simple \
    https://pypi.org/simple; do \
  echo "Try installing from $src"; \
  pip install --no-cache-dir -r requirements.txt -i $src && break; \
done
```

### Xvfb虚拟显示器配置

为了支持PDF导出功能，容器内配置了Xvfb虚拟显示器：

```bash
# 启动Xvfb虚拟显示器
RUN echo '#!/bin/bash\nXvfb :99 -screen 0 1024x768x24 -ac +extension GLX &\nexport DISPLAY=:99\nexec "$@"' > /usr/local/bin/start-xvfb.sh \
    && chmod +x /usr/local/bin/start-xvfb.sh
```

**章节来源**
- [Dockerfile](file://Dockerfile#L1-L58)
- [docker-compose.yml](file://docker-compose.yml#L4-L6)

## 容器服务配置

### 端口映射与访问控制

Web服务监听8501端口，这是Streamlit框架的默认端口：

```yaml
ports:
  - "8501:8501"
```

端口映射采用`主机端口:容器端口`格式，允许外部访问Web界面。8501端口专门用于Web应用访问，与其他服务端口（如27017、6379）隔离。

### 容器命名规范

```yaml
container_name: TradingAgents-web
```

容器名称遵循项目命名约定，便于识别和管理。这种命名方式有助于在复杂的Docker环境中快速定位特定服务。

### 命令执行配置

```yaml
command: /usr/local/bin/start-xvfb.sh python -m streamlit run web/app.py --server.address=0.0.0.0 --server.port=8501
```

命令配置确保了完整的启动流程：
1. 启动Xvfb虚拟显示器
2. 运行Streamlit应用
3. 监听所有网络接口（0.0.0.0）
4. 使用8501端口

**章节来源**
- [docker-compose.yml](file://docker-compose.yml#L5-L10)
- [Dockerfile](file://Dockerfile#L35-L37)

## 代码卷挂载与热重载

### 开发环境代码映射

```yaml
volumes:
  - .env:/app/.env
  - ./web:/app/web
  - ./tradingagents:/app/tradingagents
  - ./scripts:/app/scripts
```

这些卷挂载提供了开发环境的热重载优势：

| 挂载点 | 目标路径 | 功能 |
|--------|----------|------|
| `.env` | `/app/.env` | 环境变量配置实时更新 |
| `./web` | `/app/web` | Web应用代码热重载 |
| `./tradingagents` | `/app/tradingagents` | 核心业务逻辑热重载 |
| `./scripts` | `/app/scripts` | 辅助脚本热重载 |

### 热重载工作原理

1. **文件监控**: Streamlit内置文件监控机制
2. **自动重载**: 检测到文件变更时自动重启应用
3. **状态保持**: 会话状态在重载过程中保持
4. **开发效率**: 显著提升开发调试速度

### 生产环境与开发环境差异

生产环境通常移除代码卷挂载，使用预构建的镜像部署，确保稳定性和性能。

**章节来源**
- [docker-compose.yml](file://docker-compose.yml#L11-L16)

## 环境变量覆盖机制

### Docker专用数据库配置

```yaml
environment:
  # Docker专用数据库配置（覆盖.env中的本地配置）
  TRADINGAGENTS_MONGODB_URL: mongodb://admin:tradingagents123@mongodb:27017/tradingagents?authSource=admin
  TRADINGAGENTS_REDIS_URL: redis://:tradingagents123@redis:6379
  TRADINGAGENTS_CACHE_TYPE: redis
```

### 服务发现机制

Docker环境中的环境变量覆盖机制实现了服务发现：

```mermaid
sequenceDiagram
participant App as Web应用
participant Env as 环境变量
participant Docker as Docker网络
participant Service as 数据库服务
App->>Env : 读取TRADINGAGENTS_MONGODB_URL
Env->>Docker : 解析服务名称为容器IP
Docker->>Service : DNS解析mongodb
Service-->>Docker : 返回容器IP
Docker-->>Env : 返回解析结果
Env-->>App : 返回完整连接字符串
App->>Service : 建立数据库连接
```

**图表来源**
- [docker-compose.yml](file://docker-compose.yml#L25-L28)

### 环境变量优先级

1. **Docker环境变量** (`environment:`) - 最高优先级
2. **env_file** (`env_file:`) - 中等优先级  
3. **系统环境变量** - 最低优先级

### 关键环境变量配置

| 变量名 | 用途 | Docker值 | 本地值 |
|--------|------|----------|--------|
| `TRADINGAGENTS_MONGODB_URL` | MongoDB连接 | `mongodb://mongodb:27017/...` | `mongodb://localhost:27017/...` |
| `TRADINGAGENTS_REDIS_URL` | Redis连接 | `redis://redis:6379` | `redis://localhost:6379` |
| `DOCKER_CONTAINER` | 容器标识 | `"true"` | `""` |
| `DISPLAY` | X11显示 | `":99"` | `""` |

### 安全性考虑

1. **密码管理**: 敏感信息通过环境变量传递
2. **网络隔离**: Docker网络提供基本隔离
3. **服务发现**: 使用内部DNS解析，避免硬编码IP

**章节来源**
- [docker-compose.yml](file://docker-compose.yml#L20-L35)
- [tradingagents/config/env_utils.py](file://tradingagents/config/env_utils.py#L1-L245)

## 健康检查与重启策略

### 健康检查配置

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 60s
```

### 健康检查工作原理

```mermaid
flowchart TD
Start([容器启动]) --> Wait["等待60秒启动期"]
Wait --> FirstCheck["首次健康检查"]
FirstCheck --> CheckResult{"检查结果"}
CheckResult --> |成功| Healthy["标记为健康"]
CheckResult --> |失败| Retry["重试计数器 +1"]
Retry --> RetryCount{"重试次数 < 3?"}
RetryCount --> |是| WaitInterval["等待30秒"]
WaitInterval --> FirstCheck
RetryCount --> |否| Unhealthy["标记为不健康"]
Healthy --> Monitor["持续监控"]
Unhealthy --> Restart["触发重启"]
Monitor --> HealthCheck["每30秒检查"]
HealthCheck --> CheckResult
Restart --> Start
```

**图表来源**
- [docker-compose.yml](file://docker-compose.yml#L44-L50)

### 超时重试策略

1. **启动期**: 60秒内允许服务启动
2. **检查间隔**: 30秒执行一次健康检查
3. **超时时间**: 10秒内必须完成检查
4. **重试次数**: 最多重试3次

### 重启策略配置

```yaml
restart: unless-stopped
```

**重启策略行为**:
- **unless-stopped**: 容器异常退出时自动重启
- **保持运行**: 系统重启后不会自动启动
- **故障恢复**: 自动恢复服务可用性

### 监控指标

健康检查通过以下指标评估服务状态：
- **HTTP响应**: 检查`/_stcore/health`端点
- **响应时间**: 确保服务响应正常
- **功能完整性**: 验证核心功能可用

**章节来源**
- [docker-compose.yml](file://docker-compose.yml#L44-L52)

## 网络配置

### 自定义网络配置

```yaml
networks:
  tradingagents-network:
    driver: bridge
    name: tradingagents-network
```

### 网络隔离与通信

```mermaid
graph TB
subgraph "tradingagents-network"
subgraph "Web服务层"
Web[TradingAgents-web<br/>8501端口]
end
subgraph "数据存储层"
MongoDB[TradingAgents-mongodb<br/>27017端口]
Redis[TradingAgents-redis<br/>6379端口]
end
subgraph "管理界面层"
RedisCmd[TradingAgents-redis-commander<br/>8081端口]
MongoExp[Mongo-Express<br/>8082端口]
end
end
Internet[外部网络] --> Web
Internet --> RedisCmd
Internet --> MongoExp
Web -.-> MongoDB
Web -.-> Redis
RedisCmd -.-> Redis
MongoExp -.-> MongoDB
```

**图表来源**
- [docker-compose.yml](file://docker-compose.yml#L155-L159)

### 服务间通信

1. **内部DNS解析**: 服务名称作为主机名
2. **端口暴露**: 仅必要的端口对外暴露
3. **网络隔离**: 不同层级的服务隔离
4. **安全边界**: 防止不必要的网络访问

### 网络安全考虑

- **最小权限原则**: 仅暴露必要端口
- **内部网络**: 敏感服务在内部网络中
- **DNS隔离**: 使用内部DNS解析
- **防火墙规则**: Docker网络提供基本隔离

**章节来源**
- [docker-compose.yml](file://docker-compose.yml#L155-L159)

## 日志与配置持久化

### 日志目录挂载

```yaml
volumes:
  - ./logs:/app/logs
```

### 配置目录挂载

```yaml
volumes:
  - ./config:/app/config
```

### 持久化策略

```mermaid
graph LR
subgraph "容器内"
LogDir[logs/]
ConfigDir[config/]
end
subgraph "宿主机"
HostLogs[./logs]
HostConfig[./config]
end
subgraph "数据卷"
VolumeLogs[mongodb_data]
VolumeRedis[redis_data]
end
LogDir --> HostLogs
ConfigDir --> HostConfig
LogDir -.-> VolumeLogs
ConfigDir -.-> VolumeRedis
```

**图表来源**
- [docker-compose.yml](file://docker-compose.yml#L17-L20)

### 日志配置详解

Docker环境的日志配置针对容器化环境进行了优化：

| 配置项 | 值 | 说明 |
|--------|-----|------|
| `max-size` | `100MB` | 单个日志文件最大大小 |
| `max-file` | `3` | 保留的日志文件数量 |
| `structured` | `json` | 结构化日志格式 |
| `directory` | `/app/logs` | 日志文件存放路径 |

### 配置持久化优势

1. **配置备份**: 配置文件持久化防止丢失
2. **状态恢复**: 重启后配置自动恢复
3. **版本控制**: 配置文件可纳入版本控制
4. **环境一致性**: 不同环境使用相同配置

### 日志管理策略

```toml
[logging.handlers.file]
enabled = true
level = "DEBUG"
max_size = "100MB"
backup_count = 5
directory = "/app/logs"
```

**章节来源**
- [docker-compose.yml](file://docker-compose.yml#L17-L20)
- [config/logging_docker.toml](file://config/logging_docker.toml#L1-L100)

## 性能调优建议

### 内存优化

1. **Python缓冲**: 设置`PYTHONUNBUFFERED=1`避免缓冲
2. **字节码**: 设置`PYTHONDONTWRITEBYTECODE=1`减少磁盘I/O
3. **时区优化**: 设置`TZ=Asia/Shanghai`避免时区转换开销

### 网络优化

1. **连接池**: 合理配置数据库连接池大小
2. **超时设置**: 适当调整数据库连接超时
3. **压缩传输**: 启用HTTP压缩传输

### 存储优化

1. **SSD存储**: 使用SSD提高I/O性能
2. **数据卷优化**: 使用合适的存储驱动
3. **缓存策略**: 合理配置Redis缓存

### 并发处理

1. **Gunicorn**: 考虑使用Gunicorn替代Streamlit
2. **异步处理**: 实现异步任务队列
3. **负载均衡**: 多实例部署分散负载

## 常见部署问题排查

### 启动问题

#### 问题1: 容器启动失败
**症状**: 容器立即退出
**排查步骤**:
1. 检查Docker日志: `docker logs TradingAgents-web`
2. 验证环境变量配置
3. 检查端口冲突: `docker ps -a`

#### 问题2: 健康检查失败
**症状**: 容器持续重启
**排查步骤**:
1. 检查健康检查命令: `docker exec TradingAgents-web curl -f http://localhost:8501/_stcore/health`
2. 验证服务端口监听: `docker exec TradingAgents-web netstat -tlnp`
3. 检查依赖服务状态

### 连接问题

#### 问题3: 数据库连接失败
**症状**: 应用无法连接数据库
**排查步骤**:
1. 检查数据库服务状态: `docker ps | grep mongodb`
2. 验证网络连通性: `docker exec TradingAgents-web ping mongodb`
3. 检查连接字符串格式

#### 问题4: 端口冲突
**症状**: 无法绑定端口
**排查步骤**:
1. 检查端口占用: `netstat -tlnp | grep 8501`
2. 修改端口映射: `docker-compose.yml`
3. 重启Docker服务

### 性能问题

#### 问题5: 响应缓慢
**症状**: 页面加载时间过长
**排查步骤**:
1. 检查资源使用情况: `docker stats`
2. 分析日志找出瓶颈
3. 优化数据库查询

#### 问题6: 内存泄漏
**症状**: 容器内存持续增长
**排查步骤**:
1. 监控内存使用趋势
2. 检查代码中的资源释放
3. 考虑重启容器

### 配置问题

#### 问题7: 环境变量未生效
**症状**: 配置更改不生效
**排查步骤**:
1. 检查环境变量语法
2. 验证变量名称拼写
3. 重启容器使配置生效

#### 问题8: 权限问题
**症状**: 文件或目录访问被拒绝
**排查步骤**:
1. 检查文件权限: `ls -la`
2. 验证Docker用户权限
3. 修改文件所有权

### 调试工具

1. **日志分析**: 使用`docker logs`查看详细日志
2. **交互式调试**: 使用`docker exec -it`进入容器
3. **网络诊断**: 使用`docker network inspect`检查网络配置
4. **资源监控**: 使用`docker stats`监控资源使用

### 预防措施

1. **定期备份**: 定期备份配置和数据
2. **监控告警**: 设置关键指标监控
3. **版本控制**: 配置文件纳入版本控制
4. **文档维护**: 保持部署文档更新

**章节来源**
- [scripts/verify_docker_logs.py](file://scripts/verify_docker_logs.py#L227-L240)
- [scripts/rebuild_and_test.ps1](file://scripts/rebuild_and_test.ps1#L1-L51)