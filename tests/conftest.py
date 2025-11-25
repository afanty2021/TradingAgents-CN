"""
pytest全局配置
提供测试夹具、标记和配置
"""

import pytest
import os
import sys
from pathlib import Path
from typing import Dict, Any, Generator
import tempfile
import shutil
from unittest.mock import Mock, MagicMock

# 添加项目根目录到Python路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# 导入项目模块
from tradingagents.exceptions import TradingAgentsError
from tradingagents.config.config_manager import ConfigManager


@pytest.fixture(scope="session")
def project_root():
    """项目根目录路径"""
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def test_data_dir(project_root):
    """测试数据目录"""
    data_dir = project_root / "tests" / "fixtures"
    data_dir.mkdir(exist_ok=True)
    return data_dir


@pytest.fixture
def mock_financial_data():
    """模拟财务数据"""
    return {
        'symbol': 'TEST',
        'company_name': '测试公司',
        'market': 'test',
        'sector': 'technology',
        'revenue': {'2023': 1000.0, '2022': 900.0, '2021': 800.0},
        'net_income': {'2023': 100.0, '2022': 90.0, '2021': 80.0},
        'total_assets': {'2023': 2000.0, '2022': 1800.0, '2021': 1600.0},
        'shareholders_equity': {'2023': 1000.0, '2022': 900.0, '2021': 800.0},
        'total_debt': {'2023': 500.0, '2022': 450.0, '2021': 400.0},
        'operating_cash_flow': {'2023': 150.0, '2022': 135.0, '2021': 120.0},
        'free_cash_flow': {'2023': 120.0, '2022': 108.0, '2021': 96.0},
        'pe_ratio': 20.0,
        'pb_ratio': 2.0,
        'data_currency': 'USD'
    }


@pytest.fixture
def mock_market_data():
    """模拟市场数据"""
    return {
        'symbol': 'AAPL',
        'current_price': 150.0,
        'previous_close': 148.0,
        'change': 2.0,
        'change_percent': 1.35,
        'volume': 50000000,
        'market_cap': 3000000000000,
        'is_us': True,
        'is_china': False,
        'is_hk': False
    }


@pytest.fixture
def mock_analyst_reports():
    """模拟分析师报告"""
    return {
        'market_analyst': {
            'recommendation': '买入',
            'confidence': 75,
            'technical_indicators': {
                'rsi': 65.5,
                'macd': 0.12,
                'bollinger_position': 'upper'
            }
        },
        'fundamentals_analyst': {
            'recommendation': '买入',
            'confidence': 80,
            'financial_ratios': {
                'roe': 18.5,
                'pe_ratio': 22.3,
                'debt_to_equity': 0.45
            }
        },
        'news_analyst': {
            'recommendation': '买入',
            'confidence': 70,
            'sentiment': 'positive',
            'key_news': ['公司发布超预期财报', '获得重要合同']
        },
        'social_media_analyst': {
            'recommendation': '持有',
            'confidence': 60,
            'sentiment_score': 7.2,
            'discussion_volume': 'high'
        }
    }


@pytest.fixture
def sample_stock_symbols():
    """样本股票代码"""
    return {
        'us_stocks': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA'],
        'china_stocks': ['000001', '000858', '600519', '002415'],
        'hk_stocks': ['0700.HK', '9988.HK', '0941.HK'],
        'invalid_stocks': ['INVALID', '123456', 'TOOLONG']
    }


@pytest.fixture
def temp_config_file():
    """临时配置文件"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write('{"test": true, "debug": false}')
        temp_path = f.name

    yield temp_path

    # 清理
    os.unlink(temp_path)


@pytest.fixture
def mock_llm_response():
    """模拟LLM响应"""
    def _create_mock_response(content: str, function_calls=None):
        mock_response = Mock()
        mock_response.content = content
        mock_response.function_calls = function_calls or []
        return mock_response

    return _create_mock_response


@pytest.fixture
def mock_api_responses():
    """模拟API响应"""
    return {
        'tushare': {
            'get_stock_basic': {
                'code': '000001',
                'name': '平安银行',
                'industry': '银行',
                'area': '深圳'
            },
            'get_daily': [
                {'trade_date': '20240115', 'close': 10.50, 'volume': 1000000}
            ]
        },
        'akshare': {
            'stock_info_a': {
                '股票代码': '000001',
                '股票名称': '平安银行',
                '行业': '银行'
            },
            'stock_zh_a_hist': [
                {'日期': '2024-01-15', '收盘': 10.50, '成交量': 1000000}
            ]
        },
        'finnhub': {
            'quote': {
                'c': 150.0,
                'h': 152.0,
                'l': 148.0,
                'o': 149.0,
                'pc': 1.35
            },
            'financials': {
                'metric': {
                    'revenueTTM': 365817000000,
                    'netIncomeTTM': 94680000000
                }
            }
        },
        'yahoo': {
            'info': {
                'symbol': 'AAPL',
                'shortName': 'Apple Inc.',
                'sector': 'Technology',
                'marketCap': 3000000000000
            },
            'history': [
                {'Date': '2024-01-15', 'Close': 150.0, 'Volume': 50000000}
            ]
        }
    }


@pytest.fixture
def mock_environment():
    """模拟环境变量"""
    original_env = os.environ.copy()

    # 设置测试环境变量
    test_env = {
        'DASHSCOPE_API_KEY': 'test-dashscope-key',
        'DEEPSEEK_API_KEY': 'test-deepseek-key',
        'FINNHUB_API_KEY': 'test-finnhub-key',
        'TESTING': 'true',
        'LOG_LEVEL': 'DEBUG'
    }

    os.environ.update(test_env)

    yield test_env

    # 恢复原始环境变量
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def mock_cache():
    """模拟缓存"""
    cache_data = {}

    class MockCache:
        def get(self, key, default=None):
            return cache_data.get(key, default)

        def set(self, key, value, timeout=None):
            cache_data[key] = value

        def delete(self, key):
            cache_data.pop(key, None)

        def clear(self):
            cache_data.clear()

        def keys(self):
            return list(cache_data.keys())

    return MockCache()


# 测试标记
def pytest_configure(config):
    """配置pytest标记"""
    config.addinivalue_line(
        "markers", "unit: 标记单元测试"
    )
    config.addinivalue_line(
        "markers", "integration: 标记集成测试"
    )
    config.addinivalue_line(
        "markers", "slow: 标记慢速测试"
    )
    config.addinivalue_line(
        "markers", "network: 标记需要网络的测试"
    )
    config.addinivalue_line(
        "markers", "api: 标记API测试"
    )
    config.addinivalue_line(
        "markers", "gpu: 标记需要GPU的测试"
    )


# 测试收集钩子
def pytest_collection_modifyitems(config, items):
    """修改测试收集"""
    for item in items:
        # 自动添加标记
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)

        # 基于测试名称添加标记
        if "test_api" in item.name:
            item.add_marker(pytest.mark.api)
        if "test_network" in item.name:
            item.add_marker(pytest.mark.network)
        if "test_slow" in item.name:
            item.add_marker(pytest.mark.slow)


# 测试会话钩子
@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """自动设置测试环境"""
    # Mock环境变量
    monkeypatch.setenv("TESTING", "true")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")

    # 禁用实际的网络请求
    def mock_requests_get(*args, **kwargs):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"mock": "data"}
        return mock_response

    monkeypatch.setattr("requests.get", mock_requests_get)


# 跳过条件
def pytest_runtest_setup(item):
    """测试前设置"""
    # 检查是否需要跳过
    if item.get_closest_marker("network") and not os.getenv("ENABLE_NETWORK_TESTS"):
        pytest.skip("网络测试已禁用，使用 ENABLE_NETWORK_TESTS=1 启用")

    if item.get_closest_marker("api") and not os.getenv("ENABLE_API_TESTS"):
        pytest.skip("API测试已禁用，使用 ENABLE_API_TESTS=1 启用")


# 测试报告钩子
def pytest_html_report_title(report):
    """自定义HTML报告标题"""
    report.title = "TradingAgents-CN 测试报告"


# 性能测试标记
performance = pytest.mark.skipif(
    not os.getenv("ENABLE_PERFORMANCE_TESTS"),
    reason="性能测试已禁用，使用 ENABLE_PERFORMANCE_TESTS=1 启用"
)

# 网络测试标记
network = pytest.mark.skipif(
    not os.getenv("ENABLE_NETWORK_TESTS"),
    reason="网络测试已禁用，使用 ENABLE_NETWORK_TESTS=1 启用"
)

# API测试标记
api = pytest.mark.skipif(
    not os.getenv("ENABLE_API_TESTS"),
    reason="API测试已禁用，使用 ENABLE_API_TESTS=1 启用"
)

# GPU测试标记
gpu = pytest.mark.skipif(
    not os.getenv("ENABLE_GPU_TESTS"),
    reason="GPU测试已禁用，使用 ENABLE_GPU_TESTS=1 启用"
)

# 慢速测试标记
slow = pytest.mark.skipif(
    not os.getenv("ENABLE_SLOW_TESTS"),
    reason="慢速测试已禁用，使用 ENABLE_SLOW_TESTS=1 启用"
)


# 测试工具函数
def create_test_file(content: str, suffix: str = ".py") -> str:
    """创建测试文件"""
    with tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False) as f:
        f.write(content)
        return f.name


def assert_dict_subset(subset: Dict[str, Any], superset: Dict[str, Any]):
    """断言字典是另一个字典的子集"""
    for key, value in subset.items():
        assert key in superset, f"键 '{key}' 不存在于超集中"
        assert superset[key] == value, f"键 '{key}' 的值不匹配"


def assert_valid_financial_ratios(ratios: Dict[str, Any]):
    """断言财务比率有效"""
    required_keys = ['roe', 'net_margin', 'debt_to_equity']
    for key in required_keys:
        assert key in ratios, f"缺少必需的财务比率: {key}"
        assert isinstance(ratios[key], (int, float)), f"财务比率 {key} 必须是数字"
        assert ratios[key] >= 0, f"财务比率 {key} 必须非负"


def mock_llm_with_tools(llm_mock, tool_responses: Dict[str, Any]):
    """模拟带工具的LLM"""
    def mock_call(messages, tools=None, **kwargs):
        response = Mock()
        response.content = "Mock LLM response"

        # 模拟工具调用
        if tools:
            response.tool_calls = []
            for tool in tools:
                tool_call = {
                    'name': tool['name'],
                    'args': tool_responses.get(tool['name'], {}),
                    'id': f"call_{len(response.tool_calls)}"
                }
                response.tool_calls.append(tool_call)

        return response

    llm_mock.invoke = mock_call
    llm_mock.bind_tools.return_value = llm_mock
    return llm_mock


# 测试数据生成器
def generate_financial_data(
    symbol: str = "TEST",
    years: int = 3,
    base_revenue: float = 1000.0,
    growth_rate: float = 0.1
) -> Dict[str, Any]:
    """生成测试财务数据"""
    current_year = 2024
    data = {
        'symbol': symbol,
        'company_name': f'{symbol} Company',
        'market': 'test',
        'sector': 'technology',
        'revenue': {},
        'net_income': {},
        'total_assets': {},
        'shareholders_equity': {},
        'total_debt': {},
        'operating_cash_flow': {},
        'free_cash_flow': {}
    }

    for i in range(years):
        year = current_year - i
        revenue = base_revenue * ((1 + growth_rate) ** i)
        net_income = revenue * 0.1
        total_assets = revenue * 2
        equity = total_assets * 0.5
        debt = total_assets * 0.3

        data['revenue'][str(year)] = revenue
        data['net_income'][str(year)] = net_income
        data['total_assets'][str(year)] = total_assets
        data['shareholders_equity'][str(year)] = equity
        data['total_debt'][str(year)] = debt
        data['operating_cash_flow'][str(year)] = net_income * 1.2
        data['free_cash_flow'][str(year)] = net_income * 0.8

    return data