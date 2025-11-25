"""
财务分析器单元测试
测试FinancialAnalyzer类的各个功能
"""

import pytest
import math
from tradingagents.agents.analysts.fundamentals.financial_analyzer import (
    FinancialAnalyzer, FinancialRatios, FinancialScore
)


class TestFinancialAnalyzer:
    """财务分析器测试类"""

    def setup_method(self):
        """测试前准备"""
        self.analyzer = FinancialAnalyzer()

    def test_calculate_gross_margin(self, mock_financial_data):
        """测试毛利率计算"""
        # 测试正常情况
        gross_margin = self.analyzer._calculate_gross_margin(mock_financial_data, '2023')
        assert gross_margin == 20.0  # (200 / 1000) * 100

        # 测试零收入
        mock_financial_data.revenue['2023'] = 0
        gross_margin = self.analyzer._calculate_gross_margin(mock_financial_data, '2023')
        assert gross_margin == 0.0

        # 测试负收入
        mock_financial_data.revenue['2023'] = -1000
        gross_margin = self.analyzer._calculate_gross_margin(mock_financial_data, '2023')
        assert gross_margin == 0.0

    def test_calculate_net_margin(self, mock_financial_data):
        """测试净利率计算"""
        # 测试正常情况
        net_margin = self.analyzer._calculate_net_margin(mock_financial_data, '2023')
        assert net_margin == 10.0  # (100 / 1000) * 100

        # 测试零收入
        mock_financial_data.revenue['2023'] = 0
        net_margin = self.analyzer._calculate_net_margin(mock_financial_data, '2023')
        assert net_margin == 0.0

    def test_calculate_roe(self, mock_financial_data):
        """测试净资产收益率计算"""
        # 测试正常情况
        roe = self.analyzer._calculate_roe(mock_financial_data, '2023')
        assert roe == 10.0  # (100 / 1000) * 100

        # 测试零权益
        mock_financial_data.shareholders_equity['2023'] = 0
        roe = self.analyzer._calculate_roe(mock_financial_data, '2023')
        assert roe == 0.0

        # 测试负权益
        mock_financial_data.shareholders_equity['2023'] = -1000
        roe = self.analyzer._calculate_roe(mock_financial_data, '2023')
        assert roe == 0.0

    def test_calculate_debt_to_equity(self, mock_financial_data):
        """测试债务权益比计算"""
        # 测试正常情况
        debt_to_equity = self.analyzer._calculate_debt_to_equity(mock_financial_data, '2023')
        assert debt_to_equity == 0.5  # 500 / 1000

        # 测试零权益
        mock_financial_data.shareholders_equity['2023'] = 0
        debt_to_equity = self.analyzer._calculate_debt_to_equity(mock_financial_data, '2023')
        assert math.isinf(debt_to_equity)

    def test_calculate_revenue_growth(self, mock_financial_data):
        """测试收入增长率计算"""
        # 测试正增长
        growth = self.analyzer._calculate_revenue_growth(mock_financial_data)
        expected_growth = ((1000 - 900) / 900) * 100  # 11.11%
        assert abs(growth - expected_growth) < 0.01

        # 测试负增长
        mock_financial_data.revenue['2023'] = 800
        growth = self.analyzer._calculate_revenue_growth(mock_financial_data)
        expected_negative = ((800 - 900) / 900) * 100  # -11.11%
        assert abs(growth - expected_negative) < 0.01

        # 测试数据不足
        mock_financial_data.revenue = {'2023': 1000}
        growth = self.analyzer._calculate_revenue_growth(mock_financial_data)
        assert growth == 0.0

    def test_calculate_financial_ratios(self, mock_financial_data):
        """测试财务比率计算"""
        ratios = self.analyzer._calculate_financial_ratios(mock_financial_data)

        # 验证返回类型
        assert isinstance(ratios, FinancialRatios)

        # 验证关键比率
        assert ratios.gross_margin == 20.0
        assert ratios.net_margin == 10.0
        assert ratios.roe == 10.0
        assert ratios.debt_to_equity == 0.5
        assert ratios.revenue_growth == pytest.approx(11.11, rel=1e-2)

    def test_score_profitability(self):
        """测试盈利能力评分"""
        # 测试优秀盈利能力
        ratios = FinancialRatios(
            roe=18.0, net_margin=15.0, gross_margin=40.0,
            operating_margin=20.0, roa=12.0
        )
        score = self.analyzer._score_profitability(ratios)
        assert score >= 90  # 应该获得高分

        # 测试较差盈利能力
        ratios_poor = FinancialRatios(
            roe=3.0, net_margin=2.0, gross_margin=10.0,
            operating_margin=5.0, roa=1.0
        )
        score_poor = self.analyzer._score_profitability(ratios_poor)
        assert score_poor < 50  # 应该获得低分

    def test_score_financial_health(self):
        """测试财务健康评分"""
        # 测试优秀财务健康
        ratios = FinancialRatios(
            debt_to_equity=0.3, interest_coverage=15.0,
            debt_to_assets=20.0, operating_cash_flow_ratio=1.5
        )
        score = self.analyzer._score_financial_health(ratios)
        assert score >= 85  # 应该获得高分

        # 测试较差财务健康
        ratios_poor = FinancialRatios(
            debt_to_equity=3.0, interest_coverage=1.0,
            debt_to_assets=80.0, operating_cash_flow_ratio=0.5
        )
        score_poor = self.analyzer._score_financial_health(ratios_poor)
        assert score_poor < 50  # 应该获得低分

    def test_score_growth(self):
        """测试成长性评分"""
        # 测试优秀成长性
        ratios = FinancialRatios(
            revenue_growth=25.0, earnings_growth=30.0
        )
        score = self.analyzer._score_growth(ratios)
        assert score >= 90  # 应该获得高分

        # 测试负成长
        ratios_negative = FinancialRatios(
            revenue_growth=-10.0, earnings_growth=-20.0
        )
        score_negative = self.analyzer._score_growth(ratios_negative)
        assert score_negative <= 20  # 应该获得低分

    def test_score_valuation(self):
        """测试估值评分"""
        # 测试合理估值
        ratios = FinancialRatios(
            pe_ratio=15.0, pb_ratio=1.5, ps_ratio=2.0, ev_ebitda=8.0
        )
        score = self.analyzer._score_valuation(ratios)
        assert score >= 80  # 应该获得高分

        # 测试高估值
        ratios_high = FinancialRatios(
            pe_ratio=40.0, pb_ratio=6.0, ps_ratio=8.0, ev_ebitda=25.0
        )
        score_high = self.analyzer._score_valuation(ratios_high)
        assert score_high < 50  # 应该获得低分

    def test_calculate_financial_score(self, mock_financial_data):
        """测试财务评分计算"""
        ratios = self.analyzer._calculate_financial_ratios(mock_financial_data)
        score = self.analyzer._calculate_financial_score(mock_financial_data, ratios)

        # 验证返回类型
        assert isinstance(score, FinancialScore)

        # 验证评分范围
        assert 0 <= score.overall_score <= 100
        assert 0 <= score.profitability_score <= 100
        assert 0 <= score.financial_health_score <= 100
        assert 0 <= score.efficiency_score <= 100
        assert 0 <= score.growth_score <= 100
        assert 0 <= score.valuation_score <= 100

        # 验证优势和劣势
        assert isinstance(score.strengths, list)
        assert isinstance(score.weaknesses, list)
        assert isinstance(score.risk_factors, list)

    @pytest.mark.unit
    def test_analyze_financials_success(self, mock_financial_data):
        """测试财务分析成功情况"""
        ratios, score = self.analyzer.analyze_financials(mock_financial_data)

        # 验证返回类型
        assert isinstance(ratios, FinancialRatios)
        assert isinstance(score, FinancialScore)

        # 验证数据完整性
        assert hasattr(ratios, 'roe')
        assert hasattr(ratios, 'net_margin')
        assert hasattr(score, 'overall_score')

    @pytest.mark.unit
    def test_analyze_financials_invalid_data(self):
        """测试财务分析无效数据"""
        from tradingagents.dataflows.fundamentals.data_collector import FinancialData

        # 测试无效财务数据
        invalid_data = FinancialData(
            symbol='INVALID',
            company_name='无效公司',
            market='invalid',
            sector='invalid',
            revenue={},  # 空收入数据
            net_income={},
            total_assets={},
            shareholders_equity={},
            total_debt={},
            operating_cash_flow={},
            free_cash_flow={}
        )

        with pytest.raises(AnalysisError):
            self.analyzer.analyze_financials(invalid_data)

    @pytest.mark.unit
    def test_industry_benchmark_comparison(self, mock_financial_data):
        """测试行业基准对比"""
        # 设置特定行业的数据
        mock_financial_data.sector = 'technology'
        ratios, score = self.analyzer.analyze_financials(mock_financial_data)

        # 验证行业对比
        assert 'industry_comparison' in score.__dict__
        assert isinstance(score.industry_comparison, dict)

        # 验证包含关键指标对比
        comparison = score.industry_comparison
        expected_metrics = ['roe', 'net_margin', 'debt_to_equity', 'pe_ratio', 'revenue_growth']
        for metric in expected_metrics:
            assert metric in comparison

    @pytest.mark.unit
    def test_edge_cases(self):
        """测试边界情况"""
        # 测试极大值
        ratios = FinancialRatios(
            roe=1000.0,  # 极高ROE
            debt_to_equity=0.0,  # 零债务
            pe_ratio=1.0  # 极低PE
        )
        score = self.analyzer._calculate_financial_score(None, ratios)

        # 验证评分上限
        assert score.overall_score <= 100
        assert score.profitability_score <= 100

        # 测试负值处理
        ratios_negative = FinancialRatios(
            roe=-10.0,  # 负ROE
            net_margin=-5.0,  # 负净利率
            revenue_growth=-50.0  # 负增长
        )
        score_negative = self.analyzer._calculate_financial_score(None, ratios_negative)

        # 验证负值不会导致异常
        assert score_negative.overall_score >= 0

    @pytest.mark.unit
    def test_consistency(self, mock_financial_data):
        """测试一致性"""
        # 多次调用应该返回相同结果
        ratios1, score1 = self.analyzer.analyze_financials(mock_financial_data)
        ratios2, score2 = self.analyzer.analyze_financials(mock_financial_data)

        assert ratios1.roe == ratios2.roe
        assert ratios1.net_margin == ratios2.net_margin
        assert score1.overall_score == score2.overall_score

    @pytest.mark.unit
    def test_performance(self, mock_financial_data):
        """测试性能"""
        import time

        start_time = time.time()

        # 执行100次分析
        for _ in range(100):
            self.analyzer.analyze_financials(mock_financial_data)

        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / 100

        # 验证性能要求（每次分析应该小于100ms）
        assert avg_time < 0.1, f"平均分析时间 {avg_time:.3f}s 超过100ms"