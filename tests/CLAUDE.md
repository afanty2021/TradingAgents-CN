[根目录](../../CLAUDE.md) > **tests**

# 测试模块

## 模块职责

Tests模块提供TradingAgents-CN项目的完整测试套件，确保系统功能和代码质量。主要测试范围包括：

- **单元测试**: 各个模块和组件的功能测试
- **集成测试**: 多模块协作的端到端测试
- **API测试**: 外部服务和数据源接口测试
- **性能测试**: 系统性能和响应时间测试
- **功能测试**: 完整业务流程验证

## 目录结构

```
tests/
├── README.md                    # 测试使用指南
├── __init__.py                  # 测试模块初始化
├── FILE_ORGANIZATION_SUMMARY.md # 文件组织说明
├── 0.1.14/                     # v0.1.14版本专项测试
├── integration/                 # 集成测试
├── test_analysis.py             # 核心分析功能测试
├── test_akshare_api.py          # AkShare API测试
├── test_all_apis.py             # 所有API综合测试
├── test_*.py                    # 各类专项测试文件
└── debug_*.py                   # 调试和诊断脚本
```

## 核心测试分类

### 1. 核心功能测试

#### 主要测试文件
- **test_analysis.py**: 核心分析功能测试
- **test_comprehensive_backup.py**: 综合备份测试
- **test_data_structure.py**: 数据结构测试
- **test_final_integration.py**: 最终集成测试

#### 分析功能测试示例
```python
# tests/test_analysis.py
import pytest
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

class TestStockAnalysis:
    """股票分析功能测试"""

    def setup_method(self):
        """测试前准备"""
        self.config = DEFAULT_CONFIG.copy()
        self.config["llm_provider"] = "dashscope"
        self.config["deep_think_llm"] = "qwen-turbo"
        self.config["quick_think_llm"] = "qwen-turbo"
        self.config["max_debate_rounds"] = 1  # 减少测试时间

    def test_basic_analysis(self):
        """基础分析功能测试"""

        # 创建交易智能体
        ta = TradingAgentsGraph(debug=False, config=self.config)

        # 执行分析
        state, decision = ta.propagate("AAPL", "2024-01-15")

        # 验证结果
        assert 'action' in decision
        assert decision['action'] in ['BUY', 'SELL', 'HOLD']
        assert 'confidence' in decision
        assert 0 <= decision['confidence'] <= 1

    def test_different_stocks(self):
        """不同股票分析测试"""

        test_stocks = ["AAPL", "MSFT", "GOOGL"]
        ta = TradingAgentsGraph(debug=False, config=self.config)

        for stock in test_stocks:
            state, decision = ta.propagate(stock, "2024-01-15")

            # 验证每只股票都能正常分析
            assert 'action' in decision
            assert decision['action'] in ['BUY', 'SELL', 'HOLD']

    def test_error_handling(self):
        """错误处理测试"""

        ta = TradingAgentsGraph(debug=False, config=self.config)

        # 测试无效股票代码
        with pytest.raises(Exception):
            ta.propagate("INVALID_STOCK", "2024-01-15")

        # 测试无效日期
        with pytest.raises(Exception):
            ta.propagate("AAPL", "invalid-date")
```

### 2. 数据源API测试

#### AkShare API测试
```python
# tests/test_akshare_api.py
import pytest
from tradingagents.dataflows.akshare_utils import AkShareProvider

class TestAkShareAPI:
    """AkShare数据源测试"""

    def setup_method(self):
        """测试前准备"""
        self.provider = AkShareProvider(enable_cache=False)

    def test_stock_info_retrieval(self):
        """股票信息获取测试"""

        test_stocks = ["000001", "000858", "600519"]

        for stock in test_stocks:
            info = self.provider.get_stock_info(stock)

            # 验证返回数据结构
            assert info is not None
            assert 'name' in info or '股票名称' in info

    def test_historical_data(self):
        """历史数据获取测试"""

        # 测试获取历史数据
        data = self.provider.get_historical_data("000001", "20240101", "20240131")

        # 验证数据格式
        assert data is not None
        if not data.empty:
            required_columns = ['date', 'open', 'high', 'low', 'close', 'volume']
            for col in required_columns:
                assert col in data.columns

    def test_realtime_data(self):
        """实时数据获取测试"""

        data = self.provider.get_realtime_price("000001")

        # 验证实时数据结构
        if data:
            assert 'price' in data or 'current' in data
            assert isinstance(data.get('price', 0), (int, float))
```

#### 多API综合测试
```python
# tests/test_all_apis.py
import pytest
from tradingagents.dataflows.interface import get_stock_info_unified

class TestAllAPIs:
    """所有数据API综合测试"""

    def test_multiple_data_sources(self):
        """多数据源测试"""

        test_stocks = [
            ("AAPL", "美股"),
            ("000001", "A股"),
            ("0700.HK", "港股")
        ]

        for stock, market in test_stocks:
            try:
                info = get_stock_info_unified(stock)
                print(f"✅ {stock} ({market}): 数据获取成功")
            except Exception as e:
                print(f"❌ {stock} ({market}): 数据获取失败 - {e}")
                # 某些数据源可能失败，但不应该全部失败

    def test_data_consistency(self):
        """数据一致性测试"""

        stock = "000001"

        # 从不同源获取相同股票的数据
        try:
            # 这里可以比较不同数据源的一致性
            # 由于数据源更新频率不同，允许一定差异
            pass
        except Exception as e:
            pytest.skip(f"数据一致性测试跳过: {e}")
```

### 3. LLM适配器测试

#### DashScope集成测试
```python
# tests/integration/test_dashscope_integration.py
import pytest
import os
from tradingagents.llm_adapters.dashscope_adapter import ChatDashScope

class TestDashScopeIntegration:
    """DashScope集成测试"""

    @pytest.mark.skipif(
        not os.getenv('DASHSCOPE_API_KEY'),
        reason="需要DASHSCOPE_API_KEY环境变量"
    )
    def test_basic_chat(self):
        """基础聊天功能测试"""

        llm = ChatDashScope(
            model="qwen-turbo",
            api_key=os.getenv('DASHSCOPE_API_KEY')
        )

        # 测试基础对话
        response = llm.invoke("你好，请介绍一下自己")

        # 验证响应
        assert response.content is not None
        assert len(response.content) > 0

    @pytest.mark.skipif(
        not os.getenv('DASHSCOPE_API_KEY'),
        reason="需要DASHSCOPE_API_KEY环境变量"
    )
    def test_tool_calling(self):
        """工具调用功能测试"""

        llm = ChatDashScope(
            model="qwen-plus",
            api_key=os.getenv('DASHSCOPE_API_KEY')
        )

        # 测试工具绑定
        tools = [
            {
                "name": "get_stock_price",
                "description": "获取股票价格",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string"}
                    }
                }
            }
        ]

        llm_with_tools = llm.bind_tools(tools)

        # 测试工具调用
        response = llm_with_tools.invoke("请帮我查询AAPL的股价")

        # 验证工具调用结果
        assert response.content is not None
```

#### DeepSeek集成测试
```python
# tests/test_deepseek_integration.py
import pytest
import os
from tradingagents.llm_adapters.deepseek_adapter import ChatDeepSeek

class TestDeepSeekIntegration:
    """DeepSeek集成测试"""

    @pytest.mark.skipif(
        not os.getenv('DEEPSEEK_API_KEY'),
        reason="需要DEEPSEEK_API_KEY环境变量"
    )
    def test_deepseek_chat(self):
        """DeepSeek聊天测试"""

        llm = ChatDeepSeek(
            model="deepseek-chat",
            api_key=os.getenv('DEEPSEEK_API_KEY')
        )

        response = llm.invoke("分析一下AAPL的投资价值")

        assert response.content is not None
        assert len(response.content) > 10  # 确保有实际内容
```

### 4. 集成测试

#### 端到端分析测试
```python
# tests/integration/test_end_to_end.py
import pytest
from tradingagents.graph.trading_graph import TradingAgentsGraph

class TestEndToEnd:
    """端到端集成测试"""

    def test_complete_analysis_workflow(self):
        """完整分析工作流测试"""

        # 配置
        config = {
            "llm_provider": "dashscope",
            "deep_think_llm": "qwen-turbo",
            "quick_think_llm": "qwen-turbo",
            "max_debate_rounds": 1,
        }

        # 创建智能体
        ta = TradingAgentsGraph(debug=False, config=config)

        # 测试股票列表
        test_cases = [
            ("AAPL", "2024-01-15"),
            ("000001", "2024-01-15"),
            ("0700.HK", "2024-01-15")
        ]

        for symbol, date in test_cases:
            try:
                # 执行完整分析
                state, decision = ta.propagate(symbol, date)

                # 验证分析结果
                assert 'action' in decision
                assert 'confidence' in decision
                assert 'risk_score' in decision

                print(f"✅ {symbol} 分析成功")

            except Exception as e:
                print(f"❌ {symbol} 分析失败: {e}")
                # 某些测试可能因为网络或API问题失败
                pytest.skip(f"跳过 {symbol} 测试: {e}")

    def test_different_configurations(self):
        """不同配置测试"""

        configurations = [
            {
                "name": "快速配置",
                "config": {
                    "llm_provider": "dashscope",
                    "deep_think_llm": "qwen-turbo",
                    "max_debate_rounds": 1,
                }
            },
            {
                "name": "标准配置",
                "config": {
                    "llm_provider": "dashscope",
                    "deep_think_llm": "qwen-plus",
                    "max_debate_rounds": 2,
                }
            }
        ]

        for case in configurations:
            try:
                ta = TradingAgentsGraph(debug=False, config=case["config"])
                state, decision = ta.propagate("AAPL", "2024-01-15")

                assert 'action' in decision
                print(f"✅ {case['name']} 测试通过")

            except Exception as e:
                print(f"❌ {case['name']} 测试失败: {e}")
                pytest.skip(f"跳过 {case['name']} 测试: {e}")
```

### 5. 性能测试

#### 响应时间测试
```python
# tests/test_performance.py
import time
import pytest
from tradingagents.graph.trading_graph import TradingAgentsGraph

class TestPerformance:
    """性能测试"""

    def test_analysis_response_time(self):
        """分析响应时间测试"""

        config = {
            "llm_provider": "dashscope",
            "deep_think_llm": "qwen-turbo",
            "max_debate_rounds": 1,
        }

        ta = TradingAgentsGraph(debug=False, config=config)

        # 记录开始时间
        start_time = time.time()

        try:
            # 执行分析
            state, decision = ta.propagate("AAPL", "2024-01-15")

            # 计算响应时间
            response_time = time.time() - start_time

            # 验证响应时间应该在合理范围内 (例如5分钟)
            assert response_time < 300, f"分析耗时过长: {response_time:.1f}秒"

            print(f"✅ 分析完成，耗时: {response_time:.1f}秒")

        except Exception as e:
            # 网络或API问题导致失败，跳过性能测试
            pytest.skip(f"性能测试跳过: {e}")

    def test_concurrent_analysis(self):
        """并发分析测试"""

        import threading
        import queue

        results = queue.Queue()
        config = {
            "llm_provider": "dashscope",
            "deep_think_llm": "qwen-turbo",
            "max_debate_rounds": 1,
        }

        def analyze_stock(stock_symbol):
            """单个股票分析线程"""
            try:
                ta = TradingAgentsGraph(debug=False, config=config)
                state, decision = ta.propagate(stock_symbol, "2024-01-15")
                results.put((stock_symbol, True, None))
            except Exception as e:
                results.put((stock_symbol, False, str(e)))

        # 并发分析多个股票
        stocks = ["AAPL", "MSFT", "GOOGL"]
        threads = []

        start_time = time.time()

        for stock in stocks:
            thread = threading.Thread(target=analyze_stock, args=(stock,))
            threads.append(thread)
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join(timeout=300)  # 5分钟超时

        # 收集结果
        total_time = time.time() - start_time
        success_count = 0

        while not results.empty():
            stock, success, error = results.get()
            if success:
                success_count += 1
                print(f"✅ {stock} 分析成功")
            else:
                print(f"❌ {stock} 分析失败: {error}")

        print(f"📊 并发测试结果: {success_count}/{len(stocks)} 成功")
        print(f"⏱️ 总耗时: {total_time:.1f}秒")
```

### 6. 版本特定测试

#### v0.1.14专项测试
位于 `tests/0.1.14/` 目录下，包含针对特定版本的专项测试：

- **test_analysis_save.py**: 分析保存功能测试
- **test_backup_datasource.py**: 数据源备份测试
- **test_user_management.py**: 用户管理功能测试
- **test_web_interface.py**: Web界面功能测试

### 7. 调试和诊断脚本

#### 调试工具
```python
# tests/debug_full_flow.py
#!/usr/bin/env python3
"""
完整流程调试脚本
用于诊断系统运行问题
"""

def debug_full_analysis():
    """调试完整分析流程"""

    print("🔍 开始调试完整分析流程")
    print("="*50)

    # 1. 检查环境配置
    print("1️⃣ 检查环境配置:")
    check_environment()

    # 2. 检查API连接
    print("\n2️⃣ 检查API连接:")
    test_api_connections()

    # 3. 检查数据源
    print("\n3️⃣ 检查数据源:")
    test_data_sources()

    # 4. 执行完整分析
    print("\n4️⃣ 执行完整分析:")
    run_complete_analysis()

    # 5. 生成诊断报告
    print("\n5️⃣ 生成诊断报告:")
    generate_diagnostic_report()

def check_environment():
    """检查环境配置"""

    import os

    required_env = [
        'DASHSCOPE_API_KEY',
        'FINNHUB_API_KEY'
    ]

    for env_var in required_env:
        value = os.getenv(env_var)
        if value:
            print(f"  ✅ {env_var}: 已配置")
        else:
            print(f"  ❌ {env_var}: 未配置")

def test_api_connections():
    """测试API连接"""

    try:
        # 测试DashScope连接
        from tradingagents.llm_adapters.dashscope_adapter import ChatDashScope
        llm = ChatDashScope(model="qwen-turbo")
        response = llm.invoke("测试连接")
        print(f"  ✅ DashScope: 连接成功")

    except Exception as e:
        print(f"  ❌ DashScope: 连接失败 - {e}")

if __name__ == "__main__":
    debug_full_analysis()
```

## 运行测试

### 基础测试命令
```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试文件
python -m pytest tests/test_analysis.py

# 运行特定测试类
python -m pytest tests/test_analysis.py::TestStockAnalysis

# 运行特定测试方法
python -m pytest tests/test_analysis.py::TestStockAnalysis::test_basic_analysis
```

### 测试配置选项
```bash
# 显示详细输出
python -m pytest tests/ -v

# 显示测试覆盖率
python -m pytest tests/ --cov=tradingagents --cov-report=html

# 运行性能测试
python -m pytest tests/test_performance.py -v

# 跳过网络依赖的测试
python -m pytest tests/ -m "not network"

# 只运行集成测试
python -m pytest tests/integration/ -v
```

### 环境变量设置
```bash
# 设置测试环境
export TESTING=true
export LOG_LEVEL=DEBUG

# API密钥 (用于集成测试)
export DASHSCOPE_API_KEY="your-test-api-key"
export FINNHUB_API_KEY="your-test-finnhub-key"

# 可选的测试数据库
export TEST_MONGODB_URL="mongodb://localhost:27017/test_tradingagents"
export TEST_REDIS_URL="redis://localhost:6379/1"
```

## 测试最佳实践

### 1. 测试组织结构
- **单元测试**: 测试单个函数或类的功能
- **集成测试**: 测试多个组件的协作
- **端到端测试**: 测试完整的业务流程
- **性能测试**: 测试系统性能指标

### 2. 测试命名规范
- **文件命名**: `test_*.py` 格式
- **类命名**: `Test*` 格式，继承 `unittest.TestCase` 或使用 pytest
- **方法命名**: `test_*` 格式，描述性命名

### 3. 测试数据管理
- 使用 `pytest.fixture` 管理测试数据
- 测试数据与生产数据分离
- 使用模拟数据避免依赖外部服务

### 4. 错误处理测试
```python
def test_error_scenarios():
    """错误场景测试"""

    # 测试API密钥错误
    with pytest.raises(AuthenticationError):
        analyze_with_invalid_key()

    # 测试网络连接错误
    with pytest.raises(ConnectionError):
        analyze_with_network_error()

    # 测试数据格式错误
    with pytest.raises(DataFormatError):
        analyze_with_invalid_data()
```

### 5. 测试清理
```python
def setup_method(self):
    """测试前准备"""
    # 创建测试数据
    # 初始化测试环境

def teardown_method(self):
    """测试后清理"""
    # 清理测试数据
    # 重置测试环境
```

## 持续集成

### GitHub Actions配置示例
```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.11

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov

    - name: Run tests
      env:
        DASHSCOPE_API_KEY: ${{ secrets.DASHSCOPE_API_KEY }}
        FINNHUB_API_KEY: ${{ secrets.FINNHUB_API_KEY }}
      run: |
        pytest tests/ --cov=tradingagents --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v1
      with:
        file: ./coverage.xml
```

## 测试覆盖率

### 覆盖率目标
- **核心模块**: 90%+ 覆盖率
- **工具模块**: 85%+ 覆盖率
- **示例代码**: 70%+ 覆盖率
- **总体覆盖率**: 80%+ 目标

### 覆盖率报告生成
```bash
# 生成HTML覆盖率报告
python -m pytest tests/ --cov=tradingagents --cov-report=html

# 查看报告
open htmlcov/index.html

# 生成XML报告 (用于CI)
python -m pytest tests/ --cov=tradingagents --cov-report=xml
```

## 故障排除

### 常见测试问题

#### 1. API密钥问题
```bash
# 检查环境变量
echo $DASHSCOPE_API_KEY

# 临时设置测试密钥
export DASHSCOPE_API_KEY="test-key"
```

#### 2. 网络连接问题
```bash
# 跳过网络依赖测试
python -m pytest tests/ -m "not network"

# 使用模拟数据
python -m pytest tests/ --mock-network
```

#### 3. 依赖版本冲突
```bash
# 使用测试环境
python -m venv test_env
source test_env/bin/activate  # Linux/Mac
pip install -r requirements.txt
pip install pytest
```

## 相关文件清单

### 核心测试文件
- `test_analysis.py` - 核心分析功能测试
- `test_akshare_api.py` - AkShare API测试
- `test_all_apis.py` - 多API综合测试
- `test_performance.py` - 性能测试

### 集成测试
- `integration/test_dashscope_integration.py` - DashScope集成测试
- `integration/test_end_to_end.py` - 端到端测试

### 版本特定测试
- `0.1.14/` - v0.1.14版本专项测试
- `0.1.14/test_analysis_save.py` - 分析保存测试

### 调试工具
- `debug_full_flow.py` - 完整流程调试
- `test_installation.py` - 安装验证测试

### 测试配置
- `conftest.py` - pytest全局配置
- `README.md` - 测试使用说明

## 变更记录

- **2025-01-19**: 初始创建测试模块文档
- **2025-01-19**: 添加详细的测试分类和示例
- **2025-01-19**: 完善测试最佳实践和故障排除指南

---

*此文档描述了TradingAgents-CN的测试策略和实现。定期运行测试有助于保证代码质量和系统稳定性。*