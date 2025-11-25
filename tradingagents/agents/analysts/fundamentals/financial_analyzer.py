"""
财务分析器
对公司的财务数据进行深入分析，计算关键财务指标和比率
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import math
import logging

from tradingagents.exceptions import (
    AnalysisError, ValidationError, InsufficientDataError,
    handle_exceptions
)
from tradingagents.utils.logging_init import get_logger

logger = get_logger(__name__)


@dataclass
class FinancialRatios:
    """财务比率数据结构"""
    # 盈利能力比率
    gross_margin: float  # 毛利率 (%)
    operating_margin: float  # 营业利润率 (%)
    net_margin: float  # 净利率 (%)
    roe: float  # 净资产收益率 (%)
    roa: float  # 总资产收益率 (%)
    roic: float  # 投入资本收益率 (%)

    # 财务结构比率
    debt_to_equity: float  # 债务权益比
    debt_to_assets: float  # 资产负债率
    interest_coverage: float  # 利息保障倍数

    # 运营效率比率
    asset_turnover: float  # 资产周转率
    inventory_turnover: float  # 存货周转率
    receivables_turnover: float  # 应收账款周转率

    # 成长性比率
    revenue_growth: float  # 收入增长率 (%)
    earnings_growth: float  # 盈利增长率 (%)

    # 估值比率
    pe_ratio: float  # 市盈率
    pb_ratio: float  # 市净率
    ps_ratio: float  # 市销率
    ev_ebitda: float  # EV/EBITDA

    # 现金流比率
    operating_cash_flow_ratio: float  # 经营现金流/净利润
    free_cash_flow_ratio: float  # 自由现金流/净利润
    capex_ratio: float  # 资本支出/收入


@dataclass
class FinancialScore:
    """财务评分结果"""
    overall_score: float  # 综合评分 (0-100)
    profitability_score: float  # 盈利能力评分
    financial_health_score: float  # 财务健康评分
    efficiency_score: float  # 运营效率评分
    growth_score: float  # 成长性评分
    valuation_score: float  # 估值评分

    # 关键指标
    strengths: List[str]  # 优势
    weaknesses: List[str]  # 劣势
    risk_factors: List[str]  # 风险因素

    # 行业对比
    industry_comparison: Dict[str, float]


class FinancialAnalyzer:
    """财务分析器"""

    def __init__(self, industry_benchmarks: Optional[Dict[str, Dict[str, float]]] = None):
        """
        初始化财务分析器

        Args:
            industry_benchmarks: 行业基准数据
        """
        self.industry_benchmarks = industry_benchmarks or self._load_default_benchmarks()

    @handle_exceptions({
            ValueError: ValidationError,
            KeyError: InsufficientDataError,
            Exception: AnalysisError
        })
    def analyze_financials(self, financial_data: Any) -> Tuple[FinancialRatios, FinancialScore]:
        """
        执行财务分析

        Args:
            financial_data: 财务数据对象

        Returns:
            Tuple[FinancialRatios, FinancialScore]: 财务比率和评分

        Raises:
            ValidationError: 数据验证失败
            InsufficientDataError: 数据不足
            AnalysisError: 分析过程错误
        """
        try:
            logger.info(f"🔍 开始分析 {financial_data.symbol} 的财务数据")

            # 1. 计算财务比率
            ratios = self._calculate_financial_ratios(financial_data)

            # 2. 进行财务评分
            score = self._calculate_financial_score(financial_data, ratios)

            # 3. 生成分析洞察
            self._generate_insights(financial_data, ratios, score)

            logger.info(f"✅ {financial_data.symbol} 财务分析完成")
            return ratios, score

        except Exception as e:
            logger.error(f"❌ {financial_data.symbol} 财务分析失败: {e}")
            raise AnalysisError(f"财务分析失败: {e}", 'FINANCIAL_ANALYSIS_FAILED',
                             {'symbol': financial_data.symbol})

    def _calculate_financial_ratios(self, financial_data: Any) -> FinancialRatios:
        """计算财务比率"""
        try:
            # 获取最新年份数据
            latest_year = self._get_latest_year(financial_data)

            # 盈利能力比率
            gross_margin = self._calculate_gross_margin(financial_data, latest_year)
            operating_margin = self._calculate_operating_margin(financial_data, latest_year)
            net_margin = self._calculate_net_margin(financial_data, latest_year)
            roe = self._calculate_roe(financial_data, latest_year)
            roa = self._calculate_roa(financial_data, latest_year)
            roic = self._calculate_roic(financial_data, latest_year)

            # 财务结构比率
            debt_to_equity = self._calculate_debt_to_equity(financial_data, latest_year)
            debt_to_assets = self._calculate_debt_to_assets(financial_data, latest_year)
            interest_coverage = self._calculate_interest_coverage(financial_data, latest_year)

            # 运营效率比率
            asset_turnover = self._calculate_asset_turnover(financial_data, latest_year)
            inventory_turnover = self._calculate_inventory_turnover(financial_data, latest_year)
            receivables_turnover = self._calculate_receivables_turnover(financial_data, latest_year)

            # 成长性比率
            revenue_growth = self._calculate_revenue_growth(financial_data)
            earnings_growth = self._calculate_earnings_growth(financial_data)

            # 估值比率 (如果提供)
            pe_ratio = getattr(financial_data, 'pe_ratio', None) or 0.0
            pb_ratio = getattr(financial_data, 'pb_ratio', None) or 0.0
            ps_ratio = self._calculate_ps_ratio(financial_data, latest_year)
            ev_ebitda = getattr(financial_data, 'ev_ebitda', None) or 0.0

            # 现金流比率
            operating_cash_flow_ratio = self._calculate_operating_cash_flow_ratio(
                financial_data, latest_year)
            free_cash_flow_ratio = self._calculate_free_cash_flow_ratio(
                financial_data, latest_year)
            capex_ratio = self._calculate_capex_ratio(financial_data, latest_year)

            return FinancialRatios(
                gross_margin=gross_margin,
                operating_margin=operating_margin,
                net_margin=net_margin,
                roe=roe,
                roa=roa,
                roic=roic,
                debt_to_equity=debt_to_equity,
                debt_to_assets=debt_to_assets,
                interest_coverage=interest_coverage,
                asset_turnover=asset_turnover,
                inventory_turnover=inventory_turnover,
                receivables_turnover=receivables_turnover,
                revenue_growth=revenue_growth,
                earnings_growth=earnings_growth,
                pe_ratio=pe_ratio,
                pb_ratio=pb_ratio,
                ps_ratio=ps_ratio,
                ev_ebitda=ev_ebitda,
                operating_cash_flow_ratio=operating_cash_flow_ratio,
                free_cash_flow_ratio=free_cash_flow_ratio,
                capex_ratio=capex_ratio
            )

        except Exception as e:
            logger.error(f"计算财务比率失败: {e}")
            raise AnalysisError(f"财务比率计算失败: {e}", 'RATIO_CALCULATION_FAILED')

    def _calculate_gross_margin(self, financial_data: Any, year: str) -> float:
        """计算毛利率"""
        try:
            gross_profit = financial_data.gross_profit.get(year, 0)
            revenue = financial_data.revenue.get(year, 0)

            if revenue <= 0:
                return 0.0

            return (gross_profit / revenue) * 100

        except Exception as e:
            logger.debug(f"计算毛利率失败: {e}")
            return 0.0

    def _calculate_operating_margin(self, financial_data: Any, year: str) -> float:
        """计算营业利润率"""
        try:
            # 营业利润 = 毛利润 - 运营费用
            gross_profit = financial_data.gross_profit.get(year, 0)
            revenue = financial_data.revenue.get(year, 0)

            if revenue <= 0:
                return 0.0

            # 简化计算，实际应该从损益表获取营业利润
            operating_income = gross_profit * 0.8  # 假设80%的毛利润是营业利润

            return (operating_income / revenue) * 100

        except Exception as e:
            logger.debug(f"计算营业利润率失败: {e}")
            return 0.0

    def _calculate_net_margin(self, financial_data: Any, year: str) -> float:
        """计算净利率"""
        try:
            net_income = financial_data.net_income.get(year, 0)
            revenue = financial_data.revenue.get(year, 0)

            if revenue <= 0:
                return 0.0

            return (net_income / revenue) * 100

        except Exception as e:
            logger.debug(f"计算净利率失败: {e}")
            return 0.0

    def _calculate_roe(self, financial_data: Any, year: str) -> float:
        """计算净资产收益率 (ROE)"""
        try:
            net_income = financial_data.net_income.get(year, 0)
            shareholders_equity = financial_data.shareholders_equity.get(year, 0)

            if shareholders_equity <= 0:
                return 0.0

            return (net_income / shareholders_equity) * 100

        except Exception as e:
            logger.debug(f"计算ROE失败: {e}")
            return 0.0

    def _calculate_roa(self, financial_data: Any, year: str) -> float:
        """计算总资产收益率 (ROA)"""
        try:
            net_income = financial_data.net_income.get(year, 0)
            total_assets = financial_data.total_assets.get(year, 0)

            if total_assets <= 0:
                return 0.0

            return (net_income / total_assets) * 100

        except Exception as e:
            logger.debug(f"计算ROA失败: {e}")
            return 0.0

    def _calculate_roic(self, financial_data: Any, year: str) -> float:
        """计算投入资本收益率 (ROIC)"""
        try:
            # ROIC = NOPAT / 投入资本
            # 简化计算
            net_income = financial_data.net_income.get(year, 0)
            total_debt = financial_data.total_debt.get(year, 0)
            shareholders_equity = financial_data.shareholders_equity.get(year, 0)

            invested_capital = total_debt + shareholders_equity

            if invested_capital <= 0:
                return 0.0

            nopat = net_income * 0.75  # 假设税后营业利润

            return (nopat / invested_capital) * 100

        except Exception as e:
            logger.debug(f"计算ROIC失败: {e}")
            return 0.0

    def _calculate_debt_to_equity(self, financial_data: Any, year: str) -> float:
        """计算债务权益比"""
        try:
            total_debt = financial_data.total_debt.get(year, 0)
            shareholders_equity = financial_data.shareholders_equity.get(year, 0)

            if shareholders_equity <= 0:
                return float('inf')  # 表示高风险

            return total_debt / shareholders_equity

        except Exception as e:
            logger.debug(f"计算债务权益比失败: {e}")
            return float('inf')

    def _calculate_debt_to_assets(self, financial_data: Any, year: str) -> float:
        """计算资产负债率"""
        try:
            total_debt = financial_data.total_debt.get(year, 0)
            total_assets = financial_data.total_assets.get(year, 0)

            if total_assets <= 0:
                return 0.0

            return (total_debt / total_assets) * 100

        except Exception as e:
            logger.debug(f"计算资产负债率失败: {e}")
            return 0.0

    def _calculate_interest_coverage(self, financial_data: Any, year: str) -> float:
        """计算利息保障倍数"""
        try:
            # 简化计算：营业利润 / 利息费用
            gross_profit = financial_data.gross_profit.get(year, 0)
            total_debt = financial_data.total_debt.get(year, 0)

            # 假设平均利率为5%
            interest_expense = total_debt * 0.05

            if interest_expense <= 0:
                return float('inf')  # 表示无利息负担

            operating_income = gross_profit * 0.8

            return operating_income / interest_expense

        except Exception as e:
            logger.debug(f"计算利息保障倍数失败: {e}")
            return float('inf')

    def _calculate_asset_turnover(self, financial_data: Any, year: str) -> float:
        """计算资产周转率"""
        try:
            revenue = financial_data.revenue.get(year, 0)
            total_assets = financial_data.total_assets.get(year, 0)

            if total_assets <= 0:
                return 0.0

            return revenue / total_assets

        except Exception as e:
            logger.debug(f"计算资产周转率失败: {e}")
            return 0.0

    def _calculate_inventory_turnover(self, financial_data: Any, year: str) -> float:
        """计算存货周转率"""
        try:
            # 简化计算，需要销货成本数据
            revenue = financial_data.revenue.get(year, 0)
            total_assets = financial_data.total_assets.get(year, 0)

            # 假设存货是资产的20%
            inventory = total_assets * 0.2
            cogs = revenue * 0.7  # 假设销货成本是收入的70%

            if inventory <= 0:
                return 0.0

            return cogs / inventory

        except Exception as e:
            logger.debug(f"计算存货周转率失败: {e}")
            return 0.0

    def _calculate_receivables_turnover(self, financial_data: Any, year: str) -> float:
        """计算应收账款周转率"""
        try:
            revenue = financial_data.revenue.get(year, 0)
            total_assets = financial_data.total_assets.get(year, 0)

            # 假设应收账款是资产的15%
            receivables = total_assets * 0.15

            if receivables <= 0:
                return 0.0

            return revenue / receivables

        except Exception as e:
            logger.debug(f"计算应收账款周转率失败: {e}")
            return 0.0

    def _calculate_revenue_growth(self, financial_data: Any) -> float:
        """计算收入增长率"""
        try:
            years = sorted(financial_data.revenue.keys(), reverse=True)

            if len(years) < 2:
                return 0.0

            latest_year = years[0]
            previous_year = years[1]

            latest_revenue = financial_data.revenue[latest_year]
            previous_revenue = financial_data.revenue[previous_year]

            if previous_revenue <= 0:
                return 0.0

            growth_rate = ((latest_revenue - previous_revenue) / previous_revenue) * 100
            return growth_rate

        except Exception as e:
            logger.debug(f"计算收入增长率失败: {e}")
            return 0.0

    def _calculate_earnings_growth(self, financial_data: Any) -> float:
        """计算盈利增长率"""
        try:
            years = sorted(financial_data.net_income.keys(), reverse=True)

            if len(years) < 2:
                return 0.0

            latest_year = years[0]
            previous_year = years[1]

            latest_earnings = financial_data.net_income[latest_year]
            previous_earnings = financial_data.net_income[previous_year]

            if previous_earnings <= 0:
                return 0.0

            growth_rate = ((latest_earnings - previous_earnings) / abs(previous_earnings)) * 100
            return growth_rate

        except Exception as e:
            logger.debug(f"计算盈利增长率失败: {e}")
            return 0.0

    def _calculate_ps_ratio(self, financial_data: Any, year: str) -> float:
        """计算市销率"""
        try:
            # 需要市值数据，这里简化处理
            revenue = financial_data.revenue.get(year, 0)

            if revenue <= 0:
                return 0.0

            # 假设市销率
            return 2.0  # 默认值

        except Exception as e:
            logger.debug(f"计算市销率失败: {e}")
            return 0.0

    def _calculate_operating_cash_flow_ratio(self, financial_data: Any, year: str) -> float:
        """计算经营现金流比率"""
        try:
            operating_cash_flow = financial_data.operating_cash_flow.get(year, 0)
            net_income = financial_data.net_income.get(year, 0)

            if net_income <= 0:
                return 0.0

            return operating_cash_flow / net_income

        except Exception as e:
            logger.debug(f"计算经营现金流比率失败: {e}")
            return 0.0

    def _calculate_free_cash_flow_ratio(self, financial_data: Any, year: str) -> float:
        """计算自由现金流比率"""
        try:
            free_cash_flow = financial_data.free_cash_flow.get(year, 0)
            net_income = financial_data.net_income.get(year, 0)

            if net_income <= 0:
                return 0.0

            return free_cash_flow / net_income

        except Exception as e:
            logger.debug(f"计算自由现金流比率失败: {e}")
            return 0.0

    def _calculate_capex_ratio(self, financial_data: Any, year: str) -> float:
        """计算资本支出比率"""
        try:
            revenue = financial_data.revenue.get(year, 0)

            if revenue <= 0:
                return 0.0

            # 假设资本支出是收入的5%
            capex = revenue * 0.05

            return (capex / revenue) * 100

        except Exception as e:
            logger.debug(f"计算资本支出比率失败: {e}")
            return 0.0

    def _calculate_financial_score(self, financial_data: Any, ratios: FinancialRatios) -> FinancialScore:
        """计算财务评分"""
        try:
            # 1. 盈利能力评分 (0-100)
            profitability_score = self._score_profitability(ratios)

            # 2. 财务健康评分 (0-100)
            financial_health_score = self._score_financial_health(ratios)

            # 3. 运营效率评分 (0-100)
            efficiency_score = self._score_efficiency(ratios)

            # 4. 成长性评分 (0-100)
            growth_score = self._score_growth(ratios)

            # 5. 估值评分 (0-100)
            valuation_score = self._score_valuation(ratios)

            # 6. 综合评分
            overall_score = (
                profitability_score * 0.3 +
                financial_health_score * 0.25 +
                efficiency_score * 0.2 +
                growth_score * 0.15 +
                valuation_score * 0.1
            )

            # 7. 生成优势和劣势
            strengths, weaknesses, risk_factors = self._analyze_strengths_weaknesses(ratios)

            # 8. 行业对比
            industry_comparison = self._compare_to_industry(financial_data.sector, ratios)

            return FinancialScore(
                overall_score=overall_score,
                profitability_score=profitability_score,
                financial_health_score=financial_health_score,
                efficiency_score=efficiency_score,
                growth_score=growth_score,
                valuation_score=valuation_score,
                strengths=strengths,
                weaknesses=weaknesses,
                risk_factors=risk_factors,
                industry_comparison=industry_comparison
            )

        except Exception as e:
            logger.error(f"计算财务评分失败: {e}")
            raise AnalysisError(f"财务评分计算失败: {e}", 'FINANCIAL_SCORE_FAILED')

    def _score_profitability(self, ratios: FinancialRatios) -> float:
        """盈利能力评分"""
        score = 0.0

        # ROE评分 (权重40%)
        if ratios.roe >= 15:
            score += 40
        elif ratios.roe >= 10:
            score += 30
        elif ratios.roe >= 5:
            score += 20
        else:
            score += max(0, ratios.roe * 2)

        # 净利率评分 (权重30%)
        if ratios.net_margin >= 15:
            score += 30
        elif ratios.net_margin >= 10:
            score += 25
        elif ratios.net_margin >= 5:
            score += 15
        else:
            score += max(0, ratios.net_margin * 2)

        # 毛利率评分 (权重20%)
        if ratios.gross_margin >= 40:
            score += 20
        elif ratios.gross_margin >= 30:
            score += 15
        elif ratios.gross_margin >= 20:
            score += 10
        else:
            score += max(0, ratios.gross_margin * 0.5)

        # ROA评分 (权重10%)
        if ratios.roa >= 10:
            score += 10
        elif ratios.roa >= 5:
            score += 7
        elif ratios.roa >= 2:
            score += 4
        else:
            score += max(0, ratios.roa * 2)

        return min(100, score)

    def _score_financial_health(self, ratios: FinancialRatios) -> float:
        """财务健康评分"""
        score = 0.0

        # 债务权益比评分 (权重40%)
        if ratios.debt_to_equity <= 0.5:
            score += 40
        elif ratios.debt_to_equity <= 1.0:
            score += 30
        elif ratios.debt_to_equity <= 2.0:
            score += 20
        else:
            score += max(0, 40 - ratios.debt_to_equity * 10)

        # 利息保障倍数评分 (权重30%)
        if ratios.interest_coverage >= 10:
            score += 30
        elif ratios.interest_coverage >= 5:
            score += 25
        elif ratios.interest_coverage >= 2:
            score += 15
        else:
            score += max(0, ratios.interest_coverage * 5)

        # 资产负债率评分 (权重20%)
        if ratios.debt_to_assets <= 30:
            score += 20
        elif ratios.debt_to_assets <= 50:
            score += 15
        elif ratios.debt_to_assets <= 70:
            score += 10
        else:
            score += max(0, 20 - ratios.debt_to_assets * 0.3)

        # 经营现金流比率评分 (权重10%)
        if ratios.operating_cash_flow_ratio >= 1.2:
            score += 10
        elif ratios.operating_cash_flow_ratio >= 1.0:
            score += 8
        elif ratios.operating_cash_flow_ratio >= 0.8:
            score += 6
        else:
            score += max(0, ratios.operating_cash_flow_ratio * 8)

        return min(100, score)

    def _score_efficiency(self, ratios: FinancialRatios) -> float:
        """运营效率评分"""
        score = 0.0

        # 资产周转率评分 (权重40%)
        if ratios.asset_turnover >= 1.5:
            score += 40
        elif ratios.asset_turnover >= 1.0:
            score += 30
        elif ratios.asset_turnover >= 0.5:
            score += 20
        else:
            score += ratios.asset_turnover * 40

        # 存货周转率评分 (权重30%)
        if ratios.inventory_turnover >= 10:
            score += 30
        elif ratios.inventory_turnover >= 6:
            score += 25
        elif ratios.inventory_turnover >= 3:
            score += 15
        else:
            score += ratios.inventory_turnover * 5

        # 应收账款周转率评分 (权重20%)
        if ratios.receivables_turnover >= 12:
            score += 20
        elif ratios.receivables_turnover >= 8:
            score += 15
        elif ratios.receivables_turnover >= 4:
            score += 10
        else:
            score += ratios.receivables_turnover * 3

        # ROIC评分 (权重10%)
        if ratios.roic >= 12:
            score += 10
        elif ratios.roic >= 8:
            score += 8
        elif ratios.roic >= 4:
            score += 6
        else:
            score += max(0, ratios.roic * 1.5)

        return min(100, score)

    def _score_growth(self, ratios: FinancialRatios) -> float:
        """成长性评分"""
        score = 0.0

        # 收入增长率评分 (权重50%)
        if ratios.revenue_growth >= 20:
            score += 50
        elif ratios.revenue_growth >= 15:
            score += 40
        elif ratios.revenue_growth >= 10:
            score += 30
        elif ratios.revenue_growth >= 5:
            score += 20
        elif ratios.revenue_growth >= 0:
            score += 10
        else:
            score += max(0, 10 + ratios.revenue_growth * 2)

        # 盈利增长率评分 (权重50%)
        if ratios.earnings_growth >= 25:
            score += 50
        elif ratios.earnings_growth >= 15:
            score += 40
        elif ratios.earnings_growth >= 10:
            score += 30
        elif ratios.earnings_growth >= 5:
            score += 20
        elif ratios.earnings_growth >= 0:
            score += 10
        else:
            score += max(0, 10 + ratios.earnings_growth * 2)

        return min(100, score)

    def _score_valuation(self, ratios: FinancialRatios) -> float:
        """估值评分"""
        score = 0.0

        # PE评分 (权重40%) - 低PE更好
        if ratios.pe_ratio <= 15:
            score += 40
        elif ratios.pe_ratio <= 20:
            score += 30
        elif ratios.pe_ratio <= 25:
            score += 20
        elif ratios.pe_ratio <= 30:
            score += 10
        else:
            score += max(0, 40 - ratios.pe_ratio * 1.5)

        # PB评分 (权重30%) - 低PB更好
        if ratios.pb_ratio <= 1.5:
            score += 30
        elif ratios.pb_ratio <= 2.5:
            score += 25
        elif ratios.pb_ratio <= 3.5:
            score += 15
        elif ratios.pb_ratio <= 5.0:
            score += 10
        else:
            score += max(0, 30 - ratios.pb_ratio * 6)

        # PS评分 (权重20%) - 低PS更好
        if ratios.ps_ratio <= 2:
            score += 20
        elif ratios.ps_ratio <= 4:
            score += 15
        elif ratios.ps_ratio <= 6:
            score += 10
        else:
            score += max(0, 20 - ratios.ps_ratio * 3)

        # EV/EBITDA评分 (权重10%) - 低更好
        if ratios.ev_ebitda <= 10:
            score += 10
        elif ratios.ev_ebitda <= 15:
            score += 8
        elif ratios.ev_ebitda <= 20:
            score += 6
        else:
            score += max(0, 10 - ratios.ev_ebitda * 0.5)

        return min(100, score)

    def _analyze_strengths_weaknesses(self, ratios: FinancialRatios) -> Tuple[List[str], List[str], List[str]]:
        """分析优势和劣势"""
        strengths = []
        weaknesses = []
        risk_factors = []

        # 盈利能力分析
        if ratios.roe >= 15:
            strengths.append(f"卓越的净资产收益率 ({ratios.roe:.1f}%)")
        elif ratios.roe <= 5:
            weaknesses.append(f"净资产收益率偏低 ({ratios.roe:.1f}%)")

        if ratios.net_margin >= 15:
            strengths.append(f"优秀的净利率 ({ratios.net_margin:.1f}%)")
        elif ratios.net_margin <= 3:
            weaknesses.append(f"净利率偏低 ({ratios.net_margin:.1f}%)")

        # 财务健康分析
        if ratios.debt_to_equity <= 0.5:
            strengths.append(f"低债务权益比 ({ratios.debt_to_equity:.2f})")
        elif ratios.debt_to_equity >= 2.0:
            weaknesses.append(f"高债务权益比 ({ratios.debt_to_equity:.2f})")
            risk_factors.append("财务杠杆风险较高")

        if ratios.interest_coverage <= 2:
            risk_factors.append(f"利息保障倍数偏低 ({ratios.interest_coverage:.1f})")

        # 成长性分析
        if ratios.revenue_growth >= 15:
            strengths.append(f"强劲的收入增长 ({ratios.revenue_growth:.1f}%)")
        elif ratios.revenue_growth <= 0:
            weaknesses.append(f"收入增长停滞 ({ratios.revenue_growth:.1f}%)")

        if ratios.earnings_growth >= 20:
            strengths.append(f"盈利快速增长 ({ratios.earnings_growth:.1f}%)")
        elif ratios.earnings_growth <= -10:
            weaknesses.append(f"盈利下滑 ({ratios.earnings_growth:.1f}%)")
            risk_factors.append("盈利能力下滑风险")

        # 估值分析
        if ratios.pe_ratio <= 15:
            strengths.append(f"估值合理 (PE: {ratios.pe_ratio:.1f})")
        elif ratios.pe_ratio >= 30:
            weaknesses.append(f"估值偏高 (PE: {ratios.pe_ratio:.1f})")
            risk_factors.append("估值回调风险")

        # 运营效率分析
        if ratios.asset_turnover >= 1.5:
            strengths.append(f"资产运营效率高 ({ratios.asset_turnover:.2f})")
        elif ratios.asset_turnover <= 0.5:
            weaknesses.append(f"资产周转率低 ({ratios.asset_turnover:.2f})")

        return strengths, weaknesses, risk_factors

    def _compare_to_industry(self, sector: str, ratios: FinancialRatios) -> Dict[str, float]:
        """行业对比"""
        try:
            benchmark = self.industry_benchmarks.get(sector, {})

            comparison = {}

            # 关键指标对比
            metrics = ['roe', 'net_margin', 'debt_to_equity', 'pe_ratio', 'revenue_growth']

            for metric in metrics:
                benchmark_value = benchmark.get(metric, 0)
                current_value = getattr(ratios, metric, 0)

                if benchmark_value > 0:
                    comparison[metric] = (current_value / benchmark_value - 1) * 100
                else:
                    comparison[metric] = 0

            return comparison

        except Exception as e:
            logger.debug(f"行业对比失败: {e}")
            return {}

    def _generate_insights(self, financial_data: Any, ratios: FinancialRatios, score: FinancialScore):
        """生成分析洞察"""
        try:
            logger.debug(f"📊 {financial_data.symbol} 财务洞察:")

            logger.debug(f"  综合评分: {score.overall_score:.1f}/100")
            logger.debug(f"  盈利能力: {score.profitability_score:.1f}/100")
            logger.debug(f"  财务健康: {score.financial_health_score:.1f}/100")
            logger.debug(f"  运营效率: {score.efficiency_score:.1f}/100")
            logger.debug(f"  成长性: {score.growth_score:.1f}/100")
            logger.debug(f"  估值: {score.valuation_score:.1f}/100")

            if score.strengths:
                logger.debug(f"  优势: {', '.join(score.strengths)}")

            if score.weaknesses:
                logger.debug(f"  劣势: {', '.join(score.weaknesses)}")

            if score.risk_factors:
                logger.debug(f"  风险因素: {', '.join(score.risk_factors)}")

        except Exception as e:
            logger.debug(f"生成洞察失败: {e}")

    def _get_latest_year(self, financial_data: Any) -> str:
        """获取最新年份"""
        try:
            years = list(financial_data.revenue.keys())
            if not years:
                raise InsufficientDataError('revenue', 1, 0)

            return str(max(int(year) for year in years))

        except Exception as e:
            logger.debug(f"获取最新年份失败: {e}")
            return str(datetime.now().year - 1)

    def _load_default_benchmarks(self) -> Dict[str, Dict[str, float]]:
        """加载默认行业基准"""
        return {
            'technology': {
                'roe': 18.0,
                'net_margin': 12.0,
                'debt_to_equity': 0.3,
                'pe_ratio': 25.0,
                'revenue_growth': 15.0
            },
            'finance': {
                'roe': 12.0,
                'net_margin': 20.0,
                'debt_to_equity': 1.2,
                'pe_ratio': 12.0,
                'revenue_growth': 8.0
            },
            'healthcare': {
                'roe': 15.0,
                'net_margin': 15.0,
                'debt_to_equity': 0.5,
                'pe_ratio': 20.0,
                'revenue_growth': 10.0
            },
            'manufacturing': {
                'roe': 10.0,
                'net_margin': 8.0,
                'debt_to_equity': 0.8,
                'pe_ratio': 15.0,
                'revenue_growth': 5.0
            },
            'retail': {
                'roe': 14.0,
                'net_margin': 5.0,
                'debt_to_equity': 0.6,
                'pe_ratio': 18.0,
                'revenue_growth': 8.0
            }
        }