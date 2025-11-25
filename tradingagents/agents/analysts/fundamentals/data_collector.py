"""
基本面数据收集器
负责从多个数据源收集公司的财务基本面数据
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import logging

from tradingagents.exceptions import (
    DataFetchError, APIConnectionError, DataValidationError,
    InsufficientDataError, handle_exceptions
)
from tradingagents.utils.logging_init import get_logger

logger = get_logger(__name__)


@dataclass
class FinancialData:
    """财务数据模型"""
    symbol: str
    company_name: str
    market: str
    sector: str

    # 收入数据 (百万)
    revenue: Dict[str, float]  # 年份 -> 收入

    # 利润数据 (百万)
    net_income: Dict[str, float]  # 年份 -> 净利润
    gross_profit: Dict[str, float]  # 年份 -> 毛利润

    # 资产负债表数据 (百万)
    total_assets: Dict[str, float]
    total_debt: Dict[str, float]
    shareholders_equity: Dict[str, float]

    # 现金流数据 (百万)
    operating_cash_flow: Dict[str, float]
    free_cash_flow: Dict[str, float]

    # 关键比率
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    roe: Optional[float] = None
    roa: Optional[float] = None
    debt_to_equity: Optional[float] = None

    # 元数据
    data_currency: str = "USD"
    fiscal_year_end: Optional[str] = None
    data_sources: List[str] = None

    def __post_init__(self):
        if self.data_sources is None:
            self.data_sources = []


class FundamentalsDataCollector:
    """基本面数据收集器"""

    def __init__(self, enable_cache: bool = True):
        self.enable_cache = enable_cache
        self.cache = {}

        # 数据源优先级配置
        self.data_source_priority = {
            'china': ['tushare', 'akshare', 'fallback'],
            'hk': ['akshare', 'yahoo', 'fallback'],
            'us': ['finnhub', 'yahoo', 'fallback']
        }

    @handle_exceptions({
            APIConnectionError: DataFetchError,
            Exception: DataFetchError
        })
    def collect_financial_data(self, symbol: str, market_info: Dict[str, Any],
                            years: int = 3) -> FinancialData:
        """
        收集财务数据

        Args:
            symbol: 股票代码
            market_info: 市场信息
            years: 需要的历史年数

        Returns:
            FinancialData: 财务数据对象

        Raises:
            DataFetchError: 数据获取失败
            InsufficientDataError: 数据不足
        """
        try:
            logger.info(f"📊 开始收集 {symbol} 的基本面数据")

            # 1. 获取公司基本信息
            company_info = self._get_company_info(symbol, market_info)

            # 2. 根据市场选择数据源
            data_sources = self._select_data_sources(market_info)

            # 3. 收集各类财务数据
            financial_data = self._collect_all_financial_data(
                symbol, market_info, data_sources, years
            )

            # 4. 数据验证
            self._validate_financial_data(financial_data)

            logger.info(f"✅ 成功收集 {symbol} 基本面数据")
            return financial_data

        except Exception as e:
            logger.error(f"❌ 收集 {symbol} 基本面数据失败: {e}")
            raise DataFetchError(f"无法收集 {symbol} 财务数据: {e}",
                               'FINANCIAL_DATA_COLLECTION_FAILED',
                               {'symbol': symbol, 'market': market_info})

    def _get_company_info(self, symbol: str, market_info: Dict[str, Any]) -> Dict[str, Any]:
        """获取公司基本信息"""
        try:
            if market_info.get('is_china'):
                return self._get_china_company_info(symbol)
            elif market_info.get('is_hk'):
                return self._get_hk_company_info(symbol)
            elif market_info.get('is_us'):
                return self._get_us_company_info(symbol)
            else:
                # 默认处理
                return {
                    'symbol': symbol,
                    'name': f"股票{symbol}",
                    'market': 'unknown',
                    'sector': 'unknown'
                }
        except Exception as e:
            logger.warning(f"获取 {symbol} 公司信息失败: {e}")
            return {
                'symbol': symbol,
                'name': f"股票{symbol}",
                'market': 'unknown',
                'sector': 'unknown'
            }

    def _get_china_company_info(self, symbol: str) -> Dict[str, Any]:
        """获取中国公司信息"""
        try:
            from tradingagents.dataflows.interface import get_china_stock_info_unified
            stock_info = get_china_stock_info_unified(symbol)

            # 解析公司名称
            company_name = symbol
            if "股票名称:" in stock_info:
                company_name = stock_info.split("股票名称:")[1].split("\n")[0].strip()

            # 解析行业信息
            sector = "unknown"
            if "行业:" in stock_info:
                sector = stock_info.split("行业:")[1].split("\n")[0].strip()

            return {
                'symbol': symbol,
                'name': company_name,
                'market': 'china',
                'sector': sector
            }
        except Exception as e:
            logger.debug(f"获取中国公司信息失败: {e}")
            return {
                'symbol': symbol,
                'name': f"A股{symbol}",
                'market': 'china',
                'sector': 'unknown'
            }

    def _get_hk_company_info(self, symbol: str) -> Dict[str, Any]:
        """获取港股公司信息"""
        try:
            from tradingagents.dataflows.improved_hk_utils import get_hk_company_name_improved
            company_name = get_hk_company_name_improved(symbol)

            return {
                'symbol': symbol,
                'name': company_name,
                'market': 'hk',
                'sector': 'unknown'  # 港股行业信息需要额外API调用
            }
        except Exception as e:
            logger.debug(f"获取港股公司信息失败: {e}")
            clean_ticker = symbol.replace('.HK', '').replace('.hk', '')
            return {
                'symbol': symbol,
                'name': f"港股{clean_ticker}",
                'market': 'hk',
                'sector': 'unknown'
            }

    def _get_us_company_info(self, symbol: str) -> Dict[str, Any]:
        """获取美股公司信息"""
        # 美股公司名称映射
        us_stock_names = {
            'AAPL': '苹果公司',
            'TSLA': '特斯拉',
            'NVDA': '英伟达',
            'MSFT': '微软',
            'GOOGL': '谷歌',
            'AMZN': '亚马逊',
            'META': 'Meta',
            'NFLX': '奈飞'
        }

        company_name = us_stock_names.get(symbol.upper(), f"美股{symbol}")

        return {
            'symbol': symbol,
            'name': company_name,
            'market': 'us',
            'sector': 'unknown'  # 需要额外API调用获取行业
        }

    def _select_data_sources(self, market_info: Dict[str, Any]) -> List[str]:
        """选择数据源"""
        if market_info.get('is_china'):
            return self.data_source_priority['china']
        elif market_info.get('is_hk'):
            return self.data_source_priority['hk']
        elif market_info.get('is_us'):
            return self.data_source_priority['us']
        else:
            return ['fallback']

    def _collect_all_financial_data(self, symbol: str, market_info: Dict[str, Any],
                                  data_sources: List[str], years: int) -> FinancialData:
        """收集所有财务数据"""
        company_info = self._get_company_info(symbol, market_info)

        # 初始化财务数据对象
        financial_data = FinancialData(
            symbol=symbol,
            company_name=company_info['name'],
            market=company_info['market'],
            sector=company_info['sector'],
            revenue={},
            net_income={},
            gross_profit={},
            total_assets={},
            total_debt={},
            shareholders_equity={},
            operating_cash_flow={},
            free_cash_flow={}
        )

        # 尝试从各个数据源获取数据
        for data_source in data_sources:
            try:
                logger.debug(f"尝试从 {data_source} 获取 {symbol} 财务数据")

                if data_source == 'tushare':
                    self._collect_from_tushare(financial_data, years)
                elif data_source == 'akshare':
                    self._collect_from_akshare(financial_data, years)
                elif data_source == 'finnhub':
                    self._collect_from_finnhub(financial_data, years)
                elif data_source == 'yahoo':
                    self._collect_from_yahoo(financial_data, years)
                elif data_source == 'fallback':
                    self._collect_fallback_data(financial_data, years)

                # 标记数据源
                financial_data.data_sources.append(data_source)

                # 检查数据完整性
                if self._is_data_sufficient(financial_data, years):
                    logger.debug(f"{data_source} 提供了足够的数据")
                    break

            except Exception as e:
                logger.warning(f"从 {data_source} 获取 {symbol} 数据失败: {e}")
                continue

        return financial_data

    def _collect_from_tushare(self, financial_data: FinancialData, years: int):
        """从Tushare收集数据"""
        try:
            import tushare as ts

            # 这里需要实际的Tushare API调用
            # 由于需要API token，这里提供框架
            logger.debug("Tushare数据收集功能待实现")

        except Exception as e:
            logger.debug(f"Tushare数据收集失败: {e}")

    def _collect_from_akshare(self, financial_data: FinancialData, years: int):
        """从AkShare收集数据"""
        try:
            # 这里需要实际的AkShare API调用
            logger.debug("AkShare数据收集功能待实现")

        except Exception as e:
            logger.debug(f"AkShare数据收集失败: {e}")

    def _collect_from_finnhub(self, financial_data: FinancialData, years: int):
        """从FinnHub收集数据"""
        try:
            # 这里需要实际的FinnHub API调用
            logger.debug("FinnHub数据收集功能待实现")

        except Exception as e:
            logger.debug(f"FinnHub数据收集失败: {e}")

    def _collect_from_yahoo(self, financial_data: FinancialData, years: int):
        """从Yahoo Finance收集数据"""
        try:
            # 这里需要实际的Yahoo Finance API调用
            logger.debug("Yahoo Finance数据收集功能待实现")

        except Exception as e:
            logger.debug(f"Yahoo Finance数据收集失败: {e}")

    def _collect_fallback_data(self, financial_data: FinancialData, years: int):
        """收集降级数据（模拟数据）"""
        logger.debug(f"为 {financial_data.symbol} 生成模拟财务数据")

        current_year = datetime.now().year
        for i in range(years):
            year = current_year - i - 1

            # 生成模拟数据（实际应用中应该使用真实数据）
            financial_data.revenue[str(year)] = 1000 * (1 + 0.1 * (years - i))
            financial_data.net_income[str(year)] = 100 * (1 + 0.08 * (years - i))
            financial_data.total_assets[str(year)] = 5000 * (1 + 0.05 * (years - i))
            financial_data.shareholders_equity[str(year)] = 2000 * (1 + 0.06 * (years - i))

    def _is_data_sufficient(self, financial_data: FinancialData, years: int) -> bool:
        """检查数据是否充足"""
        # 至少需要一年的收入和净利润数据
        has_revenue = len(financial_data.revenue) > 0
        has_net_income = len(financial_data.net_income) > 0

        return has_revenue and has_net_income

    def _validate_financial_data(self, financial_data: FinancialData):
        """验证财务数据"""
        if not financial_data.revenue:
            raise InsufficientDataError(
                '收入数据', 1, 0
            )

        if not financial_data.net_income:
            raise InsufficientDataError(
                '净利润数据', 1, 0
            )

        # 验证数据合理性
        for year, revenue in financial_data.revenue.items():
            if revenue <= 0:
                raise DataValidationError(
                    'revenue', revenue, '必须大于0'
                )

        logger.debug(f"财务数据验证通过: {financial_data.symbol}")