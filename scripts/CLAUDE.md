[根目录](../../CLAUDE.md) > **scripts**

# 脚本工具模块

## 模块职责

Scripts模块包含TradingAgents-CN项目的各种辅助脚本和管理工具，主要功能包括：

- **部署管理**: Docker部署、环境配置、服务启动
- **开发工具**: 代码检查、格式化、依赖管理
- **维护工具**: 数据清理、备份恢复、性能优化
- **测试工具**: 自动化测试、集成验证、性能测试
- **用户管理**: 用户账户管理、权限配置

## 目录结构

```
scripts/
├── README.md                    # 脚本使用说明
├── USER_MANAGEMENT.md          # 用户管理指南
├── deployment/                 # 部署相关脚本
├── development/                # 开发工具脚本
├── docker/                     # Docker管理脚本
├── git/                        # Git工作流脚本
├── maintenance/                # 系统维护脚本
├── setup/                      # 初始化设置脚本
├── smart_start.ps1            # Windows智能启动
├── smart_start.sh             # Linux/Mac智能启动
└── start_web.py               # Python启动脚本
```

## 核心脚本分类

### 1. 部署管理脚本 (`deployment/`)

#### 发布管理
- **create_github_release.py**: GitHub发布创建
  - 自动生成发布说明
  - 创建Git标签和GitHub Release
  - 上传发布文件

```bash
# 创建新版本发布
python scripts/deployment/create_github_release.py \
  --version v0.1.15 \
  --title "TradingAgents-CN v0.1.15" \
  --description "智能新闻分析模块重大升级"
```

#### 版本发布示例
- **release_v0.1.3.py**: v0.1.3版本发布脚本
- **release_v0.1.9.py**: v0.1.9版本发布脚本

### 2. Docker管理脚本 (`docker/`)

#### 服务管理
- **start_docker_services.sh**: 启动Docker服务
```bash
#!/bin/bash
# 启动完整服务栈
docker-compose up -d --build

# 检查服务状态
docker-compose ps

# 等待服务就绪
sleep 10
echo "✅ Docker服务启动完成"
```

- **stop_docker_services.sh**: 停止Docker服务
```bash
#!/bin/bash
# 停止所有服务
docker-compose down

# 清理未使用的资源
docker system prune -f

echo "✅ Docker服务已停止并清理"
```

#### 初始化脚本
- **mongo-init.js**: MongoDB初始化脚本
```javascript
// MongoDB初始化
db = db.getSiblingDB('tradingagents');

// 创建用户
db.createUser({
  user: 'tradingagents',
  pwd: 'tradingagents123',
  roles: [
    { role: 'readWrite', db: 'tradingagents' }
  ]
});

// 创建索引
db.analysis_results.createIndex({ "stock": 1, "date": -1 });
db.user_activities.createIndex({ "user": 1, "timestamp": -1 });
```

#### 平台特定脚本
- **start_docker_services.bat**: Windows环境启动
- **start_services_alt_ports.bat**: 替代端口启动
- **start_services_simple.bat**: 简化启动流程

### 3. 开发工具脚本 (`development/`)

#### 开发辅助
- **fix_streamlit_watcher.py**: 修复Streamlit文件监听
```python
#!/usr/bin/env python3
"""
修复Streamlit文件监听问题
解决开发时代码变更不生效的问题
"""

def fix_streamlit_watcher():
    # 清理Streamlit缓存
    import shutil
    cache_dir = os.path.expanduser("~/.streamlit")
    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)
        print("✅ Streamlit缓存已清理")

    # 重新设置监听
    print("🔧 正在修复文件监听...")
    # 修复逻辑
```

- **download_finnhub_sample_data.py**: 下载示例数据
```python
#!/usr/bin/env python3
"""
下载FinnHub示例数据用于开发和测试
"""

def download_sample_data():
    # 下载热门股票数据
    symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA']

    for symbol in symbols:
        # 获取历史数据
        data = download_stock_data(symbol)
        save_to_cache(symbol, data)
        print(f"✅ {symbol} 数据下载完成")
```

#### 组织工具
- **organize_scripts.py**: 脚本组织整理
- **prepare_upstream_contribution.py**: 准备上游贡献

### 4. Git工作流脚本 (`git/`)

#### 分支管理
- **branch_manager.py**: Git分支管理器
```python
#!/usr/bin/env python3
"""
Git分支管理工具
自动化分支创建、合并、清理等操作
"""

class BranchManager:
    def create_feature_branch(self, feature_name):
        """创建功能分支"""
        branch_name = f"feature/{feature_name}"
        run_command(f"git checkout -b {branch_name}")
        print(f"✅ 创建功能分支: {branch_name}")

    def merge_feature_branch(self, branch_name):
        """合并功能分支"""
        run_command(f"git merge {branch_name}")
        run_command("git push origin main")
        print(f"✅ 合并分支: {branch_name}")
```

- **setup_fork_environment.sh**: 设置Fork环境
```bash
#!/bin/bash
# 设置上游仓库
git remote add upstream https://github.com/TauricResearch/TradingAgents.git

# 同步上游代码
git fetch upstream
git checkout main
git merge upstream/main

echo "✅ Fork环境设置完成"
```

#### 工作流程
- **upstream_git_workflow.sh**: 上游Git工作流
- **check_branch_overlap.py**: 检查分支重叠

### 5. 维护工具脚本 (`maintenance/`)

#### 系统维护
- **cleanup_cache.py**: 缓存清理工具
```python
#!/usr/bin/env python3
"""
系统缓存清理工具
清理过期的缓存文件和临时数据
"""

def cleanup_expired_cache(days=7):
    """清理过期缓存"""

    # 清理Redis缓存
    cleanup_redis_cache(days)

    # 清理MongoDB缓存
    cleanup_mongodb_cache(days)

    # 清理文件缓存
    cleanup_file_cache(days)

    print(f"✅ {days}天前的缓存已清理")
```

- **version_manager.py**: 版本管理器
```python
#!/usr/bin/env python3
"""
版本管理工具
自动化版本号更新和发布准备
"""

def update_version(new_version):
    """更新版本号"""

    # 更新VERSION文件
    with open('VERSION', 'w') as f:
        f.write(new_version)

    # 更新pyproject.toml
    update_pyproject_version(new_version)

    # 更新README.md中的版本信息
    update_readme_version(new_version)

    print(f"✅ 版本已更新至: {new_version}")
```

#### 数据维护
- **migrate_data_directories.py**: 数据目录迁移
- **fix_mongodb_reports.py**: 修复MongoDB报告
- **sync_upstream.py**: 同步上游更新

#### 分析工具
- **analyze_differences.ps1**: 分析代码差异
- **diagnose_empty_data.py`: 诊断空数据问题

### 6. 初始化设置脚本 (`setup/`)

#### 环境初始化
- **initialize_system.py**: 系统初始化
```python
#!/usr/bin/env python3
"""
系统环境初始化
自动配置和验证开发环境
"""

def initialize_system():
    """初始化系统环境"""

    # 检查Python版本
    check_python_version()

    # 创建必要目录
    create_directories()

    # 安装依赖
    install_dependencies()

    # 初始化数据库
    initialize_database()

    # 配置环境变量
    setup_environment()

    print("✅ 系统初始化完成")
```

- **setup_databases.py**: 数据库设置
```python
#!/usr/bin/env python3
"""
数据库初始化设置
"""

def setup_databases():
    """设置数据库连接"""

    # MongoDB设置
    setup_mongodb()

    # Redis设置
    setup_redis()

    # 创建初始数据
    create_initial_data()

    print("✅ 数据库设置完成")
```

#### 包管理
- **install_packages.bat**: Windows包安装
- **install_packages_venv.bat`: 虚拟环境包安装
- **pip_manager.bat`: PIP管理器

#### 配置工具
- **configure_pip_source.py**: 配置PIP源
- **migrate_env_to_config.py`: 环境变量迁移
- **quick_install.py`: 快速安装

### 7. 智能启动脚本

#### 跨平台启动
- **smart_start.sh**: Linux/Mac智能启动
```bash
#!/bin/bash
# 智能启动脚本 - Linux/Mac版本

echo "🚀 TradingAgents-CN 智能启动"

# 检查Docker环境
if command -v docker-compose &> /dev/null; then
    echo "🐳 检测到Docker环境，使用Docker启动"

    # 检查是否需要重建镜像
    if [ ! -f ".docker_built" ] || [ ".env" -nt ".docker_built" ]; then
        echo "🔨 检测到代码变更，重建Docker镜像"
        docker-compose build
        touch .docker_built
    fi

    docker-compose up -d
else
    echo "💻 使用本地Python环境启动"

    # 检查虚拟环境
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi

    # 启动Web应用
    python start_web.py
fi

echo "✅ 启动完成，访问 http://localhost:8501"
```

- **smart_start.ps1**: Windows智能启动
```powershell
# 智能启动脚本 - Windows PowerShell版本

Write-Host "🚀 TradingAgents-CN 智能启动"

# 检查Docker环境
if (Get-Command docker-compose -ErrorAction SilentlyContinue) {
    Write-Host "🐳 检测到Docker环境，使用Docker启动"

    # 检查是否需要重建镜像
    if (-not (Test-Path ".docker_built") -or (Get-Item ".env").LastWriteTime -gt (Get-Item ".docker_built").LastWriteTime) {
        Write-Host "🔨 检测到代码变更，重建Docker镜像"
        docker-compose build
        New-Item ".docker_built" -ItemType File
    }

    docker-compose up -d
} else {
    Write-Host "💻 使用本地Python环境启动"

    # 检查虚拟环境
    if (Test-Path "venv") {
        .\venv\Scripts\Activate.ps1
    }

    # 启动Web应用
    python start_web.py
}

Write-Host "✅ 启动完成，访问 http://localhost:8501"
```

#### Python启动
- **start_web.py**: Python启动脚本
```python
#!/usr/bin/env python3
"""
Web应用启动脚本
提供额外的启动检查和配置
"""

def start_web_app():
    """启动Web应用"""

    # 检查环境配置
    check_environment()

    # 检查依赖
    check_dependencies()

    # 启动Streamlit应用
    import subprocess
    import sys

    cmd = [
        sys.executable, "-m", "streamlit", "run",
        "web/app.py",
        "--server.address=0.0.0.0",
        "--server.port=8501"
    ]

    subprocess.run(cmd)

if __name__ == "__main__":
    start_web_app()
```

## 用户管理脚本

### 用户密码管理
- **user_password_manager.py**: 用户密码管理器
```python
#!/usr/bin/env python3
"""
用户密码和权限管理工具
"""

class UserManager:
    def create_user(self, username, password, role="user"):
        """创建新用户"""
        user_info = {
            'username': username,
            'password': self.hash_password(password),
            'role': role,
            'created_at': datetime.now().isoformat(),
            'last_login': None,
            'active': True
        }

        self.save_user(user_info)
        print(f"✅ 用户 {username} 创建成功")

    def change_password(self, username, new_password):
        """修改用户密码"""
        user_info = self.get_user(username)
        if user_info:
            user_info['password'] = self.hash_password(new_password)
            user_info['password_changed_at'] = datetime.now().isoformat()
            self.save_user(user_info)
            print(f"✅ {username} 密码修改成功")

    def list_users(self):
        """列出所有用户"""
        users = self.get_all_users()
        print("👥 用户列表:")
        for user in users:
            status = "🟢" if user['active'] else "🔴"
            print(f"  {status} {user['username']} ({user['role']})")
```

### 用户管理命令
```bash
# 创建新用户
python scripts/user_password_manager.py create newuser trader

# 修改密码
python scripts/user_password_manager.py change-password admin

# 列出用户
python scripts/user_password_manager.py list

# 删除用户
python scripts/user_password_manager.py delete olduser

# 重置为默认配置
python scripts/user_password_manager.py reset
```

## 诊断工具

### 系统状态检查
- **check_system_status.py**: 系统状态检查
```python
#!/usr/bin/env python3
"""
系统状态全面检查
"""

def check_system_status():
    """检查系统整体状态"""

    print("🔍 TradingAgents-CN 系统状态检查")
    print("=" * 50)

    # Python环境检查
    check_python_environment()

    # 依赖包检查
    check_dependencies()

    # API配置检查
    check_api_configuration()

    # 数据库连接检查
    check_database_connections()

    # 缓存系统检查
    check_cache_system()

    # 文件权限检查
    check_file_permissions()

    print("✅ 系统状态检查完成")

def check_api_configuration():
    """检查API配置"""

    required_apis = [
        ('DASHSCOPE_API_KEY', 'DashScope'),
        ('FINNHUB_API_KEY', 'FinnHub')
    ]

    print("\n🔑 API配置检查:")

    for env_var, name in required_apis:
        api_key = os.getenv(env_var)
        if api_key:
            print(f"  ✅ {name}: 已配置")
        else:
            print(f"  ❌ {name}: 未配置")
```

### 性能分析
- **log_analyzer.py**: 日志分析工具
```python
#!/usr/bin/env python3
"""
日志分析工具
分析系统日志提供性能和错误统计
"""

def analyze_logs():
    """分析系统日志"""

    # 读取日志文件
    log_file = "logs/tradingagents.log"

    # 统计错误信息
    error_count = count_log_entries(log_file, "ERROR")
    warning_count = count_log_entries(log_file, "WARNING")

    # 分析API调用统计
    api_stats = analyze_api_calls(log_file)

    # 性能指标分析
    performance_stats = analyze_performance(log_file)

    print(f"📊 日志分析结果:")
    print(f"  错误数量: {error_count}")
    print(f"  警告数量: {warning_count}")
    print(f"  API调用次数: {api_stats['total_calls']}")
```

## 开发辅助工具

### 代码质量
- **quick_syntax_check.py**: 快速语法检查
```python
#!/usr/bin/env python3
"""
快速Python语法检查
"""

def check_syntax():
    """检查Python文件语法"""

    python_files = find_python_files(".")

    for file_path in python_files:
        try:
            compile(open(file_path).read(), file_path, 'exec')
            print(f"✅ {file_path}")
        except SyntaxError as e:
            print(f"❌ {file_path}: {e}")
```

### 文档管理
- **batch_update_docs.py**: 批量更新文档
```python
#!/usr/bin/env python3
"""
批量文档更新工具
"""

def update_documentation():
    """批量更新文档"""

    # 更新版本号
    update_version_numbers()

    # 更新API文档
    update_api_documentation()

    # 生成变更日志
    generate_changelog()

    print("✅ 文档批量更新完成")
```

## 脚本使用指南

### 快速开始
```bash
# 1. 智能启动（推荐）
# Linux/Mac
./scripts/smart_start.sh

# Windows
.\scripts\smart_start.ps1

# 2. 系统检查
python scripts/check_system_status.py

# 3. 用户管理
python scripts/user_password_manager.py list
```

### 开发环境设置
```bash
# 1. 环境初始化
python scripts/setup/initialize_system.py

# 2. 依赖安装
./scripts/setup/install_packages.sh

# 3. 数据库设置
python scripts/setup/setup_databases.py

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 文件
```

### 生产环境部署
```bash
# 1. Docker部署
./scripts/docker/start_docker_services.sh

# 2. 服务检查
docker-compose ps

# 3. 日志查看
docker-compose logs -f web
```

## 故障排除

### 常见问题

#### 1. 脚本权限问题
```bash
# Linux/Mac - 添加执行权限
chmod +x scripts/*.sh
chmod +x scripts/smart_start.sh

# Windows - 设置执行策略
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### 2. Python路径问题
```bash
# 检查Python路径
which python
python --version

# 使用虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\Activate.ps1  # Windows
```

#### 3. 依赖安装失败
```bash
# 使用锁定版本安装
pip install -r requirements-lock.txt

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 相关文件清单

### 核心启动脚本
- `smart_start.sh` - Linux/Mac智能启动
- `smart_start.ps1` - Windows智能启动
- `start_web.py` - Python启动脚本

### 部署管理
- `deployment/create_github_release.py` - GitHub发布
- `docker/start_docker_services.sh` - Docker服务启动
- `docker/stop_docker_services.sh` - Docker服务停止

### 开发工具
- `development/fix_streamlit_watcher.py` - Streamlit修复
- `development/organize_scripts.py` - 脚本整理
- `development/download_finnhub_sample_data.py` - 示例数据下载

### 系统维护
- `maintenance/cleanup_cache.py` - 缓存清理
- `maintenance/version_manager.py` - 版本管理
- `maintenance/sync_upstream.py` - 上游同步

### 用户管理
- `user_password_manager.py` - 用户密码管理
- `USER_MANAGEMENT.md` - 用户管理指南

### 诊断工具
- `check_system_status.py` - 系统状态检查
- `log_analyzer.py` - 日志分析
- `diagnose_empty_data.py` - 数据诊断

### 初始化设置
- `setup/initialize_system.py` - 系统初始化
- `setup/setup_databases.py` - 数据库设置
- `setup/quick_install.py` - 快速安装

## 变更记录

- **2025-01-19**: 初始创建脚本模块文档
- **2025-01-19**: 添加详细的Docker和部署脚本说明
- **2025-01-19**: 完善用户管理和故障排除指南

---

*此文档描述了项目中所有脚本工具的使用方法。使用前请确保了解脚本的作用和潜在影响。*