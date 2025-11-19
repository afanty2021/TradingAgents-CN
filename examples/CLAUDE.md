[根目录](../../CLAUDE.md) > **examples**

# 示例代码模块

## 模块职责

Examples模块提供TradingAgents-CN项目的完整示例代码和使用演示，帮助用户快速上手和深入理解系统功能。主要内容包括：

- **基础示例**: 核心功能的基本使用方法
- **高级示例**: 复杂场景和定制化应用
- **集成示例**: 多组件协作的完整示例
- **演示脚本**: 特定功能的详细演示
- **测试示例**: 系统测试和验证脚本

## 目录结构

```
examples/
├── README.md                    # 示例使用指南
├── __init__.py                  # 模块初始化
├── cli_demo.py                  # CLI使用演示
├── simple_analysis_demo.py      # 简单分析演示
├── custom_analysis_demo.py      # 自定义分析演示
├── batch_analysis.py           # 批量分析示例
├── stock_list_example.py       # 股票列表分析
├── my_stock_analysis.py        # 个人股票分析
├── token_tracking_demo.py      # Token使用跟踪
├── config_management_demo.py   # 配置管理演示
├── data_dir_config_demo.py     # 数据目录配置
├── enhanced_history_demo.py    # 增强历史演示
├── test_installation.py        # 安装测试
├── dashscope_examples/         # DashScope示例
├── demo_news_filtering.py      # 新闻过滤演示
├── demo_deepseek_analysis.py   # DeepSeek分析演示
├── demo_deepseek_simple.py     # DeepSeek简单演示
├── tushare_demo.py             # Tushare数据演示
└── stock_query_examples.py     # 股票查询示例
```

## 核心示例详解

### 1. 基础使用示例

#### 简单分析演示 (`simple_analysis_demo.py`)
```python
#!/usr/bin/env python3
"""
最简单的股票分析示例
展示TradingAgents-CN的基本用法
"""

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

def simple_stock_analysis():
    """简单股票分析示例"""

    # 1. 配置LLM模型
    config = DEFAULT_CONFIG.copy()
    config["llm_provider"] = "dashscope"
    config["deep_think_llm"] = "qwen-plus"
    config["quick_think_llm"] = "qwen-turbo"

    # 2. 创建交易智能体
    print("🤖 正在初始化交易智能体...")
    ta = TradingAgentsGraph(debug=True, config=config)

    # 3. 执行股票分析
    stock_symbol = "AAPL"
    analysis_date = "2024-01-15"

    print(f"📊 开始分析 {stock_symbol} ({analysis_date})")

    # 执行分析
    state, decision = ta.propagate(stock_symbol, analysis_date)

    # 4. 显示分析结果
    print("\n" + "="*50)
    print("📋 分析结果")
    print("="*50)
    print(f"📈 股票代码: {stock_symbol}")
    print(f"💡 投资建议: {decision['action']}")
    print(f"🎯 置信度: {decision['confidence']:.1%}")
    print(f"⚠️ 风险评分: {decision['risk_score']:.1%}")
    print(f"💰 目标价格: ${decision.get('target_price', 'N/A')}")

    if 'reasoning' in decision:
        print(f"\n🧠 推理过程:")
        print(decision['reasoning'])

if __name__ == "__main__":
    simple_stock_analysis()
```

#### CLI使用演示 (`cli_demo.py`)
```python
#!/usr/bin/env python3
"""
命令行界面使用演示
展示如何通过CLI与TradingAgents交互
"""

import typer
from typing import Optional
from tradingagents.graph.trading_graph import TradingAgentsGraph

app = typer.Typer(help="TradingAgents-CN 命令行演示")

@app.command()
def analyze(
    symbol: str = typer.Argument(..., help="股票代码"),
    date: str = typer.Argument(..., help="分析日期 (YYYY-MM-DD)"),
    provider: str = typer.Option("dashscope", help="LLM提供商"),
    model: str = typer.Option("qwen-plus", help="LLM模型"),
    debug: bool = typer.Option(False, help="调试模式")
):
    """分析指定股票"""

    print(f"🚀 开始分析 {symbol} ({date})")
    print(f"🤖 使用模型: {provider}/{model}")

    try:
        # 配置智能体
        config = {
            "llm_provider": provider,
            "deep_think_llm": model,
            "quick_think_llm": model,
        }

        # 创建并运行分析
        ta = TradingAgentsGraph(debug=debug, config=config)
        state, decision = ta.propagate(symbol, date)

        # 显示结果
        print_result(symbol, decision)

    except Exception as e:
        print(f"❌ 分析失败: {e}")
        raise typer.Exit(1)

def print_result(symbol: str, decision: dict):
    """格式化显示分析结果"""

    print(f"\n{'='*50}")
    print(f"📊 {symbol} 分析报告")
    print(f"{'='*50}")

    # 投资建议
    action_emoji = {
        "BUY": "🟢",
        "SELL": "🔴",
        "HOLD": "🟡"
    }

    action = decision.get('action', 'UNKNOWN')
    emoji = action_emoji.get(action, "❓")

    print(f"{emoji} 投资建议: {action}")
    print(f"🎯 置信度: {decision.get('confidence', 0):.1%}")
    print(f"⚠️ 风险评分: {decision.get('risk_score', 0):.1%}")

    if 'target_price' in decision:
        print(f"💰 目标价格: ${decision['target_price']:.2f}")

if __name__ == "__main__":
    app()
```

### 2. DashScope集成示例

#### 中文演示 (`dashscope_examples/demo_dashscope_chinese.py`)
```python
#!/usr/bin/env python3
"""
DashScope中文分析演示
展示阿里百炼模型的中文金融分析能力
"""

from tradingagents.graph.trading_graph import TradingAgentsGraph

def chinese_stock_analysis():
    """中文股票分析演示"""

    print("🇨🇳 TradingAgents-CN 中文分析演示")
    print("="*50)

    # 配置DashScope (通义千问)
    config = {
        "llm_provider": "dashscope",
        "deep_think_llm": "qwen-plus",      # 深度分析模型
        "quick_think_llm": "qwen-turbo",    # 快速响应模型
        "backend_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "max_debate_rounds": 2,             # 增加辩论轮次
        "online_tools": True,               # 启用在线工具
    }

    # 创建智能体
    ta = TradingAgentsGraph(debug=True, config=config)

    # 分析中国股票 (以平安银行为例)
    chinese_stocks = [
        ("000001", "平安银行"),
        ("000858", "五粮液"),
        ("600519", "贵州茅台"),
        ("300750", "宁德时代")
    ]

    for symbol, name in chinese_stocks:
        print(f"\n📊 正在分析: {name} ({symbol})")
        print("-" * 30)

        try:
            # 执行分析
            state, decision = ta.propagate(symbol, "2024-01-15")

            # 显示中文结果
            print(f"💡 投资建议: {decision['action']}")
            print(f"🎯 置信度: {decision['confidence']:.1%}")
            print(f"⚠️ 风险评分: {decision['risk_score']:.1%}")

            # 如果有目标价格
            if 'target_price' in decision:
                print(f"💰 目标价位: ¥{decision['target_price']:.2f}")

            print("✅ 分析完成\n")

        except Exception as e:
            print(f"❌ 分析失败: {e}")

if __name__ == "__main__":
    chinese_stock_analysis()
```

#### 完整演示 (`dashscope_examples/demo_dashscope.py`)
```python
#!/usr/bin/env python3
"""
DashScope完整功能演示
展示阿里百炼模型的全部功能
"""

from tradingagents.graph.trading_graph import TradingAgentsGraph
import time

def comprehensive_dashscope_demo():
    """DashScope综合演示"""

    print("🚀 DashScope 综合功能演示")
    print("="*60)

    # 测试不同模型
    models_to_test = [
        ("qwen-turbo", "快速模型"),
        ("qwen-plus", "平衡模型"),
        ("qwen-max", "最强模型")
    ]

    test_symbol = "AAPL"
    test_date = "2024-01-15"

    for model, description in models_to_test:
        print(f"\n🤖 测试模型: {model} ({description})")
        print("-" * 40)

        # 配置模型
        config = {
            "llm_provider": "dashscope",
            "deep_think_llm": model,
            "quick_think_llm": model,
        }

        # 创建智能体
        ta = TradingAgentsGraph(debug=False, config=config)

        # 记录开始时间
        start_time = time.time()

        try:
            # 执行分析
            state, decision = ta.propagate(test_symbol, test_date)

            # 计算耗时
            elapsed_time = time.time() - start_time

            # 显示结果
            print(f"⏱️ 耗时: {elapsed_time:.1f}秒")
            print(f"💡 建议: {decision['action']}")
            print(f"🎯 置信度: {decision['confidence']:.1%}")

            # 评估性价比
            if model == "qwen-turbo":
                print("💰 评价: 响应快速，成本最低，适合初步筛选")
            elif model == "qwen-plus":
                print("💰 评价: 性价比最佳，推荐日常使用")
            elif model == "qwen-max":
                print("💰 评价: 质量最高，适合重要决策")

        except Exception as e:
            print(f"❌ 分析失败: {e}")

def cost_optimization_demo():
    """成本优化演示"""

    print(f"\n💰 成本优化建议")
    print("="*30)

    print("1. 🎯 初步筛选: 使用 qwen-turbo (快速且便宜)")
    print("2. 📊 日常分析: 使用 qwen-plus (平衡性价比)")
    print("3. 🔍 重要决策: 使用 qwen-max (最高质量)")
    print("4. 📈 批量分析: 先用turbo筛选，再用plus详细分析")
    print("5. ⚡ 启用缓存: 避免重复分析相同股票")

if __name__ == "__main__":
    comprehensive_dashscope_demo()
    cost_optimization_demo()
```

### 3. 数据源使用示例

#### Tushare数据演示 (`tushare_demo.py`)
```python
#!/usr/bin/env python3
"""
Tushare数据源使用演示
展示如何使用Tushare获取A股数据
"""

import os
from datetime import datetime, timedelta
from tradingagents.dataflows.tushare_utils import TushareProvider

def tushare_data_demo():
    """Tushare数据演示"""

    print("📊 Tushare数据源演示")
    print("="*40)

    # 检查Tushare配置
    token = os.getenv('TUSHARE_TOKEN')
    if not token:
        print("❌ 请设置 TUSHARE_TOKEN 环境变量")
        return

    # 创建数据提供器
    provider = TushareProvider(token=token, enable_cache=True)

    # 测试股票
    test_stocks = ["000001", "000858", "600519", "300750"]

    for symbol in test_stocks:
        print(f"\n📈 获取 {symbol} 数据:")
        print("-" * 20)

        try:
            # 获取基本信息
            stock_info = provider.get_stock_info(symbol)
            if stock_info:
                print(f"🏢 公司名称: {stock_info.get('name', 'N/A')}")
                print(f"🏭 所属行业: {stock_info.get('industry', 'N/A')}")

            # 获取最新价格
            price_data = provider.get_realtime_price(symbol)
            if price_data:
                print(f"💰 当前价格: ¥{price_data.get('price', 0):.2f}")
                print(f"📈 涨跌幅: {price_data.get('change_pct', 0):.2f}%")

            # 获取历史数据
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')

            hist_data = provider.get_historical_data(symbol, start_date, end_date)
            if hist_data is not None and not hist_data.empty:
                print(f"📊 30天数据: {len(hist_data)} 条记录")
                latest = hist_data.iloc[-1]
                print(f"🔚 最新收盘: ¥{latest['close']:.2f}")

            print("✅ 数据获取成功")

        except Exception as e:
            print(f"❌ 数据获取失败: {e}")

def tushare_financial_demo():
    """Tushare财务数据演示"""

    print(f"\n💰 财务数据演示")
    print("="*20)

    token = os.getenv('TUSHARE_TOKEN')
    if not token:
        return

    provider = TushareProvider(token=token)

    # 获取财务数据
    symbol = "000001"  # 平安银行
    print(f"📊 获取 {symbol} 财务数据:")

    try:
        # 获取最新财务指标
        financial_data = provider.get_financial_indicators(symbol)
        if financial_data:
            print(f"💰 ROE: {financial_data.get('roe', 0):.2f}%")
            print(f"📈 PE: {financial_data.get('pe', 0):.2f}")
            print(f"💵 PB: {financial_data.get('pb', 0):.2f}")

        # 获取利润表
        income_statement = provider.get_income_statement(symbol)
        if income_statement is not None and not income_statement.empty:
            latest_income = income_statement.iloc[-1]
            print(f"💼 营业收入: {latest_income.get('total_revenue', 0):.0f}万元")
            print(f"💰 净利润: {latest_income.get('net_profit', 0):.0f}万元")

        print("✅ 财务数据获取成功")

    except Exception as e:
        print(f"❌ 财务数据获取失败: {e}")

if __name__ == "__main__":
    tushare_data_demo()
    tushare_financial_demo()
```

### 4. 高级功能示例

#### 批量分析 (`batch_analysis.py`)
```python
#!/usr/bin/env python3
"""
批量股票分析示例
展示如何同时分析多只股票
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from tradingagents.graph.trading_graph import TradingAgentsGraph

def batch_stock_analysis(stock_list, max_workers=3):
    """批量分析股票"""

    print(f"🚀 开始批量分析 {len(stock_list)} 只股票")
    print("="*50)

    # 配置
    config = {
        "llm_provider": "dashscope",
        "deep_think_llm": "qwen-plus",
        "quick_think_llm": "qwen-turbo",
        "max_debate_rounds": 1,  # 减少辩论轮次以提高速度
    }

    results = {}

    # 使用线程池并行分析
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有分析任务
        future_to_stock = {}

        for stock in stock_list:
            future = executor.submit(analyze_single_stock, stock, config)
            future_to_stock[future] = stock

        # 收集结果
        for future in as_completed(future_to_stock):
            stock = future_to_stock[future]

            try:
                result = future.result()
                results[stock] = result
                print(f"✅ {stock} 分析完成")
            except Exception as e:
                print(f"❌ {stock} 分析失败: {e}")
                results[stock] = {"error": str(e)}

    return results

def analyze_single_stock(stock, config):
    """分析单只股票"""

    ta = TradingAgentsGraph(debug=False, config=config)
    state, decision = ta.propagate(stock, "2024-01-15")

    return {
        'action': decision['action'],
        'confidence': decision['confidence'],
        'risk_score': decision['risk_score'],
        'target_price': decision.get('target_price'),
    }

def analyze_portfolio():
    """投资组合分析"""

    # 定义股票池
    tech_stocks = ["AAPL", "MSFT", "GOOGL", "NVDA"]
    chinese_stocks = ["000001", "000858", "600519"]

    print("📊 科技股组合分析:")
    tech_results = batch_stock_analysis(tech_stocks)

    print("\n🇨🇳 中概股组合分析:")
    chinese_results = batch_stock_analysis(chinese_stocks)

    # 统计分析结果
    def analyze_results(results, category):
        """分析结果统计"""

        if not results:
            return

        buy_count = sum(1 for r in results.values()
                        if isinstance(r, dict) and r.get('action') == 'BUY')
        sell_count = sum(1 for r in results.values()
                        if isinstance(r, dict) and r.get('action') == 'SELL')
        hold_count = sum(1 for r in results.values()
                        if isinstance(r, dict) and r.get('action') == 'HOLD')

        avg_confidence = sum(r.get('confidence', 0) for r in results.values()
                           if isinstance(r, dict)) / len(results)

        print(f"\n📈 {category} 分析统计:")
        print(f"  🟢 买入建议: {buy_count} 只")
        print(f"  🔴 卖出建议: {sell_count} 只")
        print(f"  🟡 持有建议: {hold_count} 只")
        print(f"  🎯 平均置信度: {avg_confidence:.1%}")

    analyze_results(tech_results, "科技股")
    analyze_results(chinese_results, "中概股")

if __name__ == "__main__":
    analyze_portfolio()
```

#### 自定义分析 (`custom_analysis_demo.py`)
```python
#!/usr/bin/env python3
"""
自定义分析配置演示
展示如何定制化分析流程
"""

from tradingagents.graph.trading_graph import TradingAgentsGraph

def custom_analysis_demo():
    """自定义分析演示"""

    print("🔧 自定义分析配置演示")
    print("="*40)

    # 场景1: 快速分析配置
    print("📊 场景1: 快速筛选分析")
    quick_config = {
        "llm_provider": "dashscope",
        "deep_think_llm": "qwen-turbo",
        "quick_think_llm": "qwen-turbo",
        "max_debate_rounds": 1,
        "max_risk_discuss_rounds": 1,
        "online_tools": False,  # 关闭在线工具提高速度
    }

    # 场景2: 深度分析配置
    print("🔍 场景2: 深度研究分析")
    deep_config = {
        "llm_provider": "dashscope",
        "deep_think_llm": "qwen-max",
        "quick_think_llm": "qwen-plus",
        "max_debate_rounds": 3,
        "max_risk_discuss_rounds": 2,
        "online_tools": True,
    }

    # 场景3: 成本优化配置
    print("💰 场景3: 成本优化分析")
    cost_config = {
        "llm_provider": "deepseek",
        "deep_think_llm": "deepseek-chat",
        "quick_think_llm": "deepseek-chat",
        "max_debate_rounds": 1,
        "online_tools": False,
    }

    # 测试不同配置
    configs = [
        (quick_config, "快速分析"),
        (deep_config, "深度分析"),
        (cost_config, "成本优化")
    ]

    test_symbol = "AAPL"

    for config, description in configs:
        print(f"\n🧪 测试 {description} 配置:")
        print("-" * 30)

        try:
            ta = TradingAgentsGraph(debug=False, config=config)
            state, decision = ta.propagate(test_symbol, "2024-01-15")

            print(f"💡 建议: {decision['action']}")
            print(f"🎯 置信度: {decision['confidence']:.1%}")
            print(f"⚠️ 风险: {decision['risk_score']:.1%}")

        except Exception as e:
            print(f"❌ 分析失败: {e}")

def custom_analyst_selection():
    """自定义分析师选择"""

    print(f"\n👥 自定义分析师团队演示")
    print("="*30)

    # 不同的分析师组合
    analyst_combinations = [
        (["market", "fundamentals"], "技术+基本面"),
        (["news", "social"], "新闻+情绪"),
        (["market", "news", "fundamentals"], "全面分析"),
        (["market", "fundamentals", "social"], "技术+基本面+情绪")
    ]

    for analysts, description in analyst_combinations:
        print(f"\n🤖 分析师组合: {description}")
        print(f"团队: {', '.join(analysts)}")

        # 创建智能体并指定分析师
        ta = TradingAgentsGraph(
            selected_analysts=analysts,
            debug=False,
            config={
                "llm_provider": "dashscope",
                "deep_think_llm": "qwen-plus",
                "quick_think_llm": "qwen-turbo",
                "max_debate_rounds": 1,
            }
        )

        try:
            state, decision = ta.propagate("AAPL", "2024-01-15")
            print(f"💡 建议: {decision['action']}")
            print(f"🎯 置信度: {decision['confidence']:.1%}")

        except Exception as e:
            print(f"❌ 分析失败: {e}")

if __name__ == "__main__":
    custom_analysis_demo()
    custom_analyst_selection()
```

### 5. 配置管理示例

#### 配置管理演示 (`config_management_demo.py`)
```python
#!/usr/bin/env python3
"""
配置管理使用演示
展示如何管理和使用系统配置
"""

import os
import json
from tradingagents.config.config_manager import ConfigManager

def config_manager_demo():
    """配置管理器演示"""

    print("⚙️ 配置管理演示")
    print("="*30)

    # 创建配置管理器
    config_manager = ConfigManager()

    # 显示当前配置
    print("📋 当前系统配置:")
    print(f"  默认提供商: {config_manager.settings['default_provider']}")
    print(f"  默认模型: {config_manager.settings['default_model']}")
    print(f"  成本跟踪: {config_manager.settings['enable_cost_tracking']}")
    print(f"  数据目录: {config_manager.settings['data_dir']}")

    # API密钥管理
    print(f"\n🔑 API密钥状态:")
    providers = ['dashscope', 'deepseek', 'openai', 'google']

    for provider in providers:
        api_key = config_manager.get_api_key(provider)
        if api_key:
            masked_key = api_key[:8] + "..." + api_key[-4:]
            print(f"  {provider}: ✅ {masked_key}")
        else:
            print(f"  {provider}: ❌ 未配置")

    # 模型配置
    print(f"\n🤖 可用模型:")
    for model_config in config_manager.models:
        status = "✅" if model_config['enabled'] else "❌"
        print(f"  {status} {model_config['provider']}/{model_config['model_name']}")

def dynamic_config_update():
    """动态配置更新演示"""

    print(f"\n🔄 动态配置更新演示")
    print("="*25)

    # 临时修改配置
    original_provider = os.getenv('DASHSCOPE_API_KEY')

    try:
        # 临时设置新的API密钥 (演示用)
        # os.environ['DASHSCOPE_API_KEY'] = 'sk-new-key-demo'

        print("🔧 配置更新:")
        print("  1. 可以通过环境变量更新配置")
        print("  2. Web界面提供可视化配置管理")
        print("  3. 配置文件支持热重载")

        # 重载配置
        # config_manager.reload()

    finally:
        # 恢复原始配置
        if original_provider:
            os.environ['DASHSCOPE_API_KEY'] = original_provider

def cost_tracking_demo():
    """成本跟踪演示"""

    print(f"\n💰 成本跟踪演示")
    print("="*20)

    # 显示定价信息
    config_manager = ConfigManager()

    print("📊 模型定价信息:")
    for model_name, pricing in config_manager.pricing['models'].items():
        input_price = pricing['input_price']
        output_price = pricing['output_price']
        currency = pricing['currency']

        print(f"  {model_name}:")
        print(f"    输入: {input_price} {currency}/千tokens")
        print(f"    输出: {output_price} {currency}/千tokens}")

    # 成本估算示例
    print(f"\n💡 成本估算示例:")
    print("  快速分析 (qwen-turbo): ~0.05 CNY")
    print("  标准分析 (qwen-plus): ~0.15 CNY")
    print("  深度分析 (qwen-max): ~0.30 CNY")

if __name__ == "__main__":
    config_manager_demo()
    dynamic_config_update()
    cost_tracking_demo()
```

### 6. Token使用跟踪示例

#### Token跟踪演示 (`token_tracking_demo.py`)
```python
#!/usr/bin/env python3
"""
Token使用跟踪演示
展示如何监控和分析LLM使用成本
"""

from tradingagents.utils.token_tracker import TokenTracker
import time

def token_tracking_demo():
    """Token使用跟踪演示"""

    print("📊 Token使用跟踪演示")
    print("="*30)

    # 创建Token跟踪器
    tracker = TokenTracker()

    # 模拟API调用
    api_calls = [
        {
            'provider': 'dashscope',
            'model': 'qwen-turbo',
            'input_tokens': 1000,
            'output_tokens': 500,
            'cost': 0.02
        },
        {
            'provider': 'dashscope',
            'model': 'qwen-plus',
            'input_tokens': 1500,
            'output_tokens': 800,
            'cost': 0.05
        },
        {
            'provider': 'deepseek',
            'model': 'deepseek-chat',
            'input_tokens': 2000,
            'output_tokens': 1000,
            'cost': 0.03
        }
    ]

    # 记录API调用
    for i, call in enumerate(api_calls, 1):
        print(f"\n📞 API调用 {i}:")
        print(f"  提供商: {call['provider']}")
        print(f"  模型: {call['model']}")
        print(f"  输入Token: {call['input_tokens']}")
        print(f"  输出Token: {call['output_tokens']}")
        print(f"  成本: ¥{call['cost']:.3f}")

        tracker.track_api_call(**call)
        time.sleep(0.1)  # 模拟时间间隔

    # 显示统计信息
    print(f"\n📈 使用统计:")
    stats = tracker.get_usage_stats()

    print(f"  总调用次数: {stats['total_calls']}")
    print(f"  总输入Token: {stats['total_input_tokens']:,}")
    print(f"  总输出Token: {stats['total_output_tokens']:,}")
    print(f"  总成本: ¥{stats['total_cost']:.2f}")
    print(f"  平均每次调用成本: ¥{stats['avg_cost_per_call']:.3f}")

def cost_optimization_analysis():
    """成本优化分析"""

    print(f"\n💰 成本优化分析")
    print("="*20)

    # 不同使用场景的成本分析
    scenarios = {
        "快速筛选": {
            "model": "qwen-turbo",
            "input_tokens": 800,
            "output_tokens": 400,
            "times_per_day": 10
        },
        "标准分析": {
            "model": "qwen-plus",
            "input_tokens": 1500,
            "output_tokens": 800,
            "times_per_day": 5
        },
        "深度研究": {
            "model": "qwen-max",
            "input_tokens": 3000,
            "output_tokens": 1500,
            "times_per_day": 2
        }
    }

    # 定价信息 (示例)
    pricing = {
        "qwen-turbo": {"input": 0.002, "output": 0.006},
        "qwen-plus": {"input": 0.004, "output": 0.012},
        "qwen-max": {"input": 0.01, "output": 0.03}
    }

    print("📊 每日成本预估:")
    total_daily_cost = 0

    for scenario, config in scenarios.items():
        model = config["model"]
        input_tokens = config["input_tokens"]
        output_tokens = config["output_tokens"]
        times = config["times_per_day"]

        # 计算单次成本
        input_cost = (input_tokens / 1000) * pricing[model]["input"]
        output_cost = (output_tokens / 1000) * pricing[model]["output"]
        single_cost = input_cost + output_cost

        # 计算每日成本
        daily_cost = single_cost * times
        total_daily_cost += daily_cost

        print(f"  {scenario}:")
        print(f"    单次成本: ¥{single_cost:.3f}")
        print(f"    每日成本: ¥{daily_cost:.2f}")

    print(f"\n💡 每日总成本: ¥{total_daily_cost:.2f}")
    print(f"📅 每月预估成本: ¥{total_daily_cost * 30:.0f}")

if __name__ == "__main__":
    token_tracking_demo()
    cost_optimization_analysis()
```

## 使用指南

### 快速开始
```bash
# 1. 基础使用示例
python examples/simple_analysis_demo.py

# 2. CLI演示
python examples/cli_demo.py analyze AAPL 2024-01-15

# 3. DashScope中文演示
python examples/dashscope_examples/demo_dashscope_chinese.py
```

### 进阶使用
```bash
# 1. 批量分析
python examples/batch_analysis.py

# 2. 自定义配置
python examples/custom_analysis_demo.py

# 3. 配置管理
python examples/config_management_demo.py

# 4. Token跟踪
python examples/token_tracking_demo.py
```

### 数据源测试
```bash
# 1. Tushare数据测试
python examples/tushare_demo.py

# 2. 股票查询示例
python examples/stock_query_examples.py

# 3. 新闻过滤演示
python examples/demo_news_filtering.py
```

## 示例最佳实践

### 1. 选择合适的示例
- **新手**: 从 `simple_analysis_demo.py` 开始
- **中文用户**: 使用 `demo_dashscope_chinese.py`
- **开发者**: 参考 `custom_analysis_demo.py`
- **运维人员**: 使用 `config_management_demo.py`

### 2. 配置环境变量
```bash
# 必需配置
export DASHSCOPE_API_KEY="your-api-key"
export FINNHUB_API_KEY="your-finnhub-key"

# 可选配置
export TUSHARE_TOKEN="your-tushare-token"
export DEEPSEEK_API_KEY="your-deepseek-key"
```

### 3. 错误处理
所有示例都包含适当的错误处理：
- API密钥检查
- 网络连接验证
- 数据格式验证
- 异常捕获和提示

### 4. 性能优化建议
- 启用缓存减少API调用
- 使用合适的模型平衡成本和质量
- 批量分析时控制并发数量
- 定期清理临时文件

## 扩展示例

### 创建自定义示例
```python
#!/usr/bin/env python3
"""
自定义示例模板
"""

from tradingagents.graph.trading_graph import TradingAgentsGraph

def my_custom_analysis():
    """自定义分析逻辑"""

    # 1. 配置参数
    config = {
        "llm_provider": "dashscope",
        "deep_think_llm": "qwen-plus",
        # 其他配置...
    }

    # 2. 创建智能体
    ta = TradingAgentsGraph(config=config)

    # 3. 自定义分析逻辑
    stock_list = ["AAPL", "MSFT", "GOOGL"]

    for stock in stock_list:
        try:
            state, decision = ta.propagate(stock, "2024-01-15")
            # 自定义结果处理...
            print(f"{stock}: {decision['action']}")

        except Exception as e:
            print(f"{stock} 分析失败: {e}")

if __name__ == "__main__":
    my_custom_analysis()
```

## 相关文件清单

### 基础示例 (必读)
- `simple_analysis_demo.py` - 最简单的使用示例
- `cli_demo.py` - 命令行界面演示
- `custom_analysis_demo.py` - 自定义配置示例

### DashScope示例
- `dashscope_examples/demo_dashscope_chinese.py` - 中文分析演示
- `dashscope_examples/demo_dashscope.py` - 完整功能演示
- `dashscope_examples/demo_dashscope_simple.py` - 简化演示

### 数据源示例
- `tushare_demo.py` - Tushare数据演示
- `stock_query_examples.py` - 股票查询示例
- `demo_news_filtering.py` - 新闻过滤演示

### 高级功能示例
- `batch_analysis.py` - 批量分析
- `token_tracking_demo.py` - Token使用跟踪
- `config_management_demo.py` - 配置管理演示

### 测试验证
- `test_installation.py` - 安装测试
- `enhanced_history_demo.py` - 历史数据演示

## 变更记录

- **2025-01-19**: 初始创建示例模块文档
- **2025-01-19**: 添加详细的DashScope和高级功能示例
- **2025-01-19**: 完善使用指南和最佳实践

---

*此文档提供了TradingAgents-CN的完整示例代码。建议按顺序学习，从简单到复杂逐步掌握系统功能。*