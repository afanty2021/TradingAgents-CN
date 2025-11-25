"""
估值模型
提供多种估值方法，包括DCF、相对估值、资产基础估值等
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
class DCFParameters:
    """DCF模型参数"""
    # 增长率假设
    revenue_growth_rate: float  # 收入增长率 (%)
    terminal_growth_rate: float  # 永续增长率 (%)
    high_growth_years: int  # 高增长期年数
    transition_years: int  # 过渡期年数

    # 盈利能力假设
    operating_margin: float  # 营业利润率 (%)
    tax_rate: float  # 所得税率 (%)
    wacc: float  # 加权平均资本成本 (%)

    # 营运资本假设
    revenue_to_capex: float  # 收入到资本支出比例
    revenue_to_wc: float  # 收入到营运资本比例

    # 其他假设
    risk_free_rate: float  # 无风险利率 (%)
    equity_risk_premium: float  # 股权风险溢价 (%)
    beta: float  # Beta系数


@dataclass
class RelativeValuationData:
    """相对估值数据"""
    pe_ratio: float
    pb_ratio: float
    ps_ratio: float
    ev_ebitda: float
    ev_revenue: float

    # 行业比较数据
    industry_pe: float
    industry_pb: float
    industry_ps: float
    industry_ev_ebitda: float

    # 历史估值数据
    historical_pe: List[float]
    historical_pb: List[float]
    historical_ps: List[float]


@dataclass
class ValuationResult:
    """估值结果"""
    # 估值方法结果
    dcf_value: float  # DCF估值
    dcf_value_per_share: float  # 每股DCF价值
    relative_value: float  # 相对估值
    asset_value: float  # 资产基础估值

    # 综合估值
    fair_value: float  # 公允价值
    fair_value_range: Tuple[float, float]  # 公允价值区间
    confidence_level: float  # 置信度 (0-100)

    # 估值分析
    upside_potential: float  # 上行潜力 (%)
    valuation_signal: str  # 估值信号 (低估/合理/高估)
    key_assumptions: List[str]  # 关键假设
    sensitivity_analysis: Dict[str, List[float]]  # 敏感性分析

    # 元数据
    current_price: float  # 当前股价
    currency: str  # 货币
    valuation_date: str  # 估值日期


class ValuationModel:
    """估值模型类"""

    def __init__(self):
        # 默认估值参数
        self.default_dcf_params = DCFParameters(
            revenue_growth_rate=10.0,
            terminal_growth_rate=3.0,
            high_growth_years=5,
            transition_years=5,
            operating_margin=15.0,
            tax_rate=25.0,
            wacc=10.0,
            revenue_to_capex=0.05,
            revenue_to_wc=0.15,
            risk_free_rate=3.0,
            equity_risk_premium=5.5,
            beta=1.0
        )

        # 行业估值倍数基准
        self.industry_benchmarks = {
            'technology': {'pe': 25.0, 'pb': 4.0, 'ps': 6.0, 'ev_ebitda': 15.0},
            'finance': {'pe': 12.0, 'pb': 1.2, 'ps': 3.0, 'ev_ebitda': 10.0},
            'healthcare': {'pe': 20.0, 'pb': 3.0, 'ps': 5.0, 'ev_ebitda': 12.0},
            'manufacturing': {'pe': 15.0, 'pb': 2.0, 'ps': 2.5, 'ev_ebitda': 8.0},
            'retail': {'pe': 18.0, 'pb': 2.5, 'ps': 1.5, 'ev_ebitda': 10.0},
            'utilities': {'pe': 15.0, 'pb': 1.5, 'ps': 2.0, 'ev_ebitda': 8.0},
            'energy': {'pe': 12.0, 'pb': 1.8, 'ps': 2.0, 'ev_ebitda': 8.0}
        }

    @handle_exceptions({
            ValueError: ValidationError,
            KeyError: InsufficientDataError,
            Exception: AnalysisError
        })
    def value_company(self, financial_data: Any, current_price: float,
                      shares_outstanding: float, industry: str = 'unknown',
                      custom_dcf_params: Optional[DCFParameters] = None) -> ValuationResult:
        """
        执行综合估值

        Args:
            financial_data: 财务数据
            current_price: 当前股价
            shares_outstanding: 流通股数
            industry: 行业分类
            custom_dcf_params: 自定义DCF参数

        Returns:
            ValuationResult: 估值结果

        Raises:
            ValidationError: 数据验证失败
            InsufficientDataError: 数据不足
            AnalysisError: 估值过程错误
        """
        try:
            logger.info(f"💰 开始对 {financial_data.symbol} 进行估值分析")

            # 1. 数据验证
            self._validate_valuation_inputs(financial_data, current_price, shares_outstanding)

            # 2. DCF估值
            dcf_result = self._perform_dcf_valuation(financial_data, custom_dcf_params)

            # 3. 相对估值
            relative_result = self._perform_relative_valuation(financial_data, industry)

            # 4. 资产基础估值
            asset_result = self._perform_asset_valuation(financial_data)

            # 5. 综合估值
            fair_value, confidence = self._calculate_fair_value(
                dcf_result, relative_result, asset_result, financial_data
            )

            # 6. 计算上行潜力
            upside_potential = ((fair_value - current_price) / current_price) * 100

            # 7. 估值信号判断
            valuation_signal = self._determine_valuation_signal(fair_value, current_price, confidence)

            # 8. 敏感性分析
            sensitivity = self._perform_sensitivity_analysis(
                financial_data, custom_dcf_params or self.default_dcf_params
            )

            # 9. 关键假设
            key_assumptions = self._extract_key_assumptions(
                custom_dcf_params or self.default_dcf_params,
                relative_result,
                financial_data
            )

            result = ValuationResult(
                dcf_value=dcf_result['enterprise_value'],
                dcf_value_per_share=dcf_result['value_per_share'],
                relative_value=relative_result['implied_value'],
                asset_value=asset_result['asset_value'],
                fair_value=fair_value,
                fair_value_range=self._calculate_value_range(
                    fair_value, confidence, sensitivity
                ),
                confidence_level=confidence,
                upside_potential=upside_potential,
                valuation_signal=valuation_signal,
                key_assumptions=key_assumptions,
                sensitivity_analysis=sensitivity,
                current_price=current_price,
                currency=financial_data.data_currency,
                valuation_date=self._get_current_date()
            )

            logger.info(f"✅ {financial_data.symbol} 估值分析完成: {valuation_signal}")
            return result

        except Exception as e:
            logger.error(f"❌ {financial_data.symbol} 估值分析失败: {e}")
            raise AnalysisError(f"估值分析失败: {e}", 'VALUATION_ANALYSIS_FAILED',
                             {'symbol': financial_data.symbol})

    def _validate_valuation_inputs(self, financial_data: Any, current_price: float,
                                   shares_outstanding: float):
        """验证估值输入数据"""
        if current_price <= 0:
            raise ValidationError('current_price', current_price, '必须大于0')

        if shares_outstanding <= 0:
            raise ValidationError('shares_outstanding', shares_outstanding, '必须大于0')

        # 检查必要的财务数据
        required_fields = ['revenue', 'net_income', 'total_assets', 'shareholders_equity']
        for field in required_fields:
            if not hasattr(financial_data, field) or not getattr(financial_data, field):
                raise InsufficientDataError(field, 1, 0)

        logger.debug(f"✅ 估值输入数据验证通过: {financial_data.symbol}")

    def _perform_dcf_valuation(self, financial_data: Any,
                              dcf_params: Optional[DCFParameters] = None) -> Dict[str, float]:
        """执行DCF估值"""
        try:
            params = dcf_params or self.default_dcf_params

            logger.debug(f"🔢 开始DCF估值 - WACC: {params.wacc}%, 增长率: {params.revenue_growth_rate}%")

            # 获取最新财务数据
            latest_year = self._get_latest_year(financial_data)
            current_revenue = financial_data.revenue.get(latest_year, 0)
            current_operating_income = current_revenue * (params.operating_margin / 100)
            current_tax = current_operating_income * (params.tax_rate / 100)
            current_noplat = current_operating_income - current_tax

            # 计算自由现金流
            current_capex = current_revenue * params.revenue_to_capex
            current_wc_change = current_revenue * params.revenue_to_wc
            current_fcf = current_noplat - current_capex - current_wc_change

            # DCF预测期现金流
            fcf_projections = []
            revenue = current_revenue

            # 高增长期
            for year in range(params.high_growth_years):
                revenue *= (1 + params.revenue_growth_rate / 100)
                operating_income = revenue * (params.operating_margin / 100)
                tax = operating_income * (params.tax_rate / 100)
                nopolat = operating_income - tax
                capex = revenue * params.revenue_to_capex
                wc_change = revenue * params.revenue_to_wc - current_revenue * params.revenue_to_wc
                fcf = nopolat - capex - wc_change

                fcf_projections.append(fcf)
                current_revenue = revenue

            # 过渡期 (增长率递减)
            for year in range(params.transition_years):
                growth_rate = params.revenue_growth_rate - (
                    (params.revenue_growth_rate - params.terminal_growth_rate) *
                    (year + 1) / params.transition_years
                )
                revenue *= (1 + growth_rate / 100)
                operating_income = revenue * (params.operating_margin / 100)
                tax = operating_income * (params.tax_rate / 100)
                nopolat = operating_income - tax
                capex = revenue * params.revenue_to_capex
                wc_change = revenue * params.revenue_to_wc - current_revenue * params.revenue_to_wc
                fcf = nopolat - capex - wc_change

                fcf_projections.append(fcf)
                current_revenue = revenue

            # 永续价值
            terminal_fcf = current_fcf * (1 + params.terminal_growth_rate / 100)
            terminal_value = terminal_fcf / ((params.wacc - params.terminal_growth_rate) / 100)

            # 折现现金流
            pv_fcf = 0
            for i, fcf in enumerate(fcf_projections, 1):
                discount_factor = (1 + params.wacc / 100) ** i
                pv_fcf += fcf / discount_factor

            # 折现永续价值
            pv_terminal = terminal_value / (
                (1 + params.wacc / 100) ** len(fcf_projections)
            )

            # 企业价值
            enterprise_value = pv_fcf + pv_terminal

            # 计算股权价值 (简化处理)
            total_debt = financial_data.total_debt.get(latest_year, 0)
            cash_equivalents = 0  # 需要从财务数据获取
            equity_value = enterprise_value - total_debt + cash_equivalents

            # 假设股数 (实际应该从数据获取)
            shares_outstanding = 1000000000  # 10亿股

            value_per_share = equity_value / shares_outstanding

            result = {
                'enterprise_value': enterprise_value,
                'equity_value': equity_value,
                'value_per_share': value_per_share,
                'pv_fcf': pv_fcf,
                'pv_terminal': pv_terminal,
                'terminal_value': terminal_value
            }

            logger.debug(f"🔢 DCF结果: 企业价值={enterprise_value:.0f}, 每股价值={value_per_share:.2f}")
            return result

        except Exception as e:
            logger.error(f"DCF估值失败: {e}")
            raise AnalysisError(f"DCF估值失败: {e}", 'DCF_VALUATION_FAILED')

    def _perform_relative_valuation(self, financial_data: Any,
                                  industry: str) -> Dict[str, float]:
        """执行相对估值"""
        try:
            logger.debug(f"📊 开始相对估值 - 行业: {industry}")

            # 获取当前估值倍数
            current_pe = getattr(financial_data, 'pe_ratio', 0) or 0
            current_pb = getattr(financial_data, 'pb_ratio', 0) or 0
            current_ps = getattr(financial_data, 'ps_ratio', 0) or 0
            current_ev_ebitda = getattr(financial_data, 'ev_ebitda', 0) or 0

            # 获取行业基准
            industry_bench = self.industry_benchmarks.get(industry, {
                'pe': 18.0, 'pb': 2.0, 'ps': 3.0, 'ev_ebitda': 10.0
            })

            # 获取最新财务指标
            latest_year = self._get_latest_year(financial_data)
            eps = financial_data.net_income.get(latest_year, 0) / 1000000000  # 假设10亿股
            book_value_per_share = financial_data.shareholders_equity.get(latest_year, 0) / 1000000000
            sales_per_share = financial_data.revenue.get(latest_year, 0) / 1000000000
            ebitda = financial_data.net_income.get(latest_year, 0) * 1.2  # 简化处理

            # 基于行业倍数的估值
            pe_based_value = eps * industry_bench['pe']
            pb_based_value = book_value_per_share * industry_bench['pb']
            ps_based_value = sales_per_share * industry_bench['ps']
            ev_ebitda_based_value = ebitda / industry_bench['ev_ebitda'] / 1000000000

            # 加权平均估值 (权重可以根据行业调整)
            weights = {
                'pe': 0.4,
                'pb': 0.2,
                'ps': 0.2,
                'ev_ebitda': 0.2
            }

            implied_value = (
                pe_based_value * weights['pe'] +
                pb_based_value * weights['pb'] +
                ps_based_value * weights['ps'] +
                ev_ebitda_based_value * weights['ev_ebitda']
            )

            result = {
                'implied_value': implied_value,
                'pe_based_value': pe_based_value,
                'pb_based_value': pb_based_value,
                'ps_based_value': ps_based_value,
                'ev_ebitda_based_value': ev_ebitda_based_value,
                'current_pe': current_pe,
                'current_pb': current_pb,
                'current_ps': current_ps,
                'industry_pe': industry_bench['pe'],
                'industry_pb': industry_bench['pb'],
                'industry_ps': industry_bench['ps'],
                'industry_ev_ebitda': industry_bench['ev_ebitda']
            }

            logger.debug(f"📊 相对估值结果: {implied_value:.2f}")
            return result

        except Exception as e:
            logger.error(f"相对估值失败: {e}")
            raise AnalysisError(f"相对估值失败: {e}", 'RELATIVE_VALUATION_FAILED')

    def _perform_asset_valuation(self, financial_data: Any) -> Dict[str, float]:
        """执行资产基础估值"""
        try:
            logger.debug(f"🏢 开始资产基础估值")

            latest_year = self._get_latest_year(financial_data)

            # 账务数据 (百万)
            total_assets = financial_data.total_assets.get(latest_year, 0)
            total_debt = financial_data.total_debt.get(latest_year, 0)
            shareholders_equity = financial_data.shareholders_equity.get(latest_year, 0)

            # 调整资产价值 (考虑资产质量)
            # 简化处理，实际应该根据行业特点调整
            asset_quality_adjustment = 0.9  # 90%的账面价值
            adjusted_assets = total_assets * asset_quality_adjustment

            # 调整负债价值
            liability_adjustment = 1.0  # 100%的账面价值
            adjusted_liabilities = total_debt * liability_adjustment

            # 净资产价值
            net_asset_value = adjusted_assets - adjusted_liabilities

            # 假设股数
            shares_outstanding = 1000000000  # 10亿股

            asset_value_per_share = net_asset_value / shares_outstanding

            # 考虑无形资产和商誉
            intangible_adjustment = 1.1  # 10%的溢价
            adjusted_asset_value = asset_value_per_share * intangible_adjustment

            result = {
                'asset_value': adjusted_asset_value,
                'net_asset_value': net_asset_value,
                'total_assets': total_assets,
                'adjusted_assets': adjusted_assets,
                'total_debt': total_debt,
                'shareholders_equity': shareholders_equity
            }

            logger.debug(f"🏢 资产估值结果: {adjusted_asset_value:.2f}")
            return result

        except Exception as e:
            logger.error(f"资产估值失败: {e}")
            raise AnalysisError(f"资产估值失败: {e}", 'ASSET_VALUATION_FAILED')

    def _calculate_fair_value(self, dcf_result: Dict, relative_result: Dict,
                            asset_result: Dict, financial_data: Any) -> Tuple[float, float]:
        """计算公允价值"""
        try:
            # 各估值方法结果
            dcf_value = dcf_result['value_per_share']
            relative_value = relative_result['implied_value']
            asset_value = asset_result['asset_value']

            # 权重分配 (可以根据行业和公司特点调整)
            weights = {
                'dcf': 0.5,      # DCF估值权重
                'relative': 0.35,  # 相对估值权重
                'asset': 0.15     # 资产估值权重
            }

            # 加权平均
            fair_value = (
                dcf_value * weights['dcf'] +
                relative_value * weights['relative'] +
                asset_value * weights['asset']
            )

            # 计算置信度 (基于各方法的一致性)
            values = [dcf_value, relative_value, asset_value]
            mean_value = sum(values) / len(values)
            variance = sum((v - mean_value) ** 2 for v in values) / len(values)
            std_dev = math.sqrt(variance)

            # 置信度计算：标准差越小，置信度越高
            if mean_value > 0:
                coefficient_of_variation = std_dev / mean_value
                confidence = max(0, min(100, 100 - coefficient_of_variation * 100))
            else:
                confidence = 0

            logger.debug(f"⚖️ 公允价值: {fair_value:.2f}, 置信度: {confidence:.1f}%")
            return fair_value, confidence

        except Exception as e:
            logger.error(f"计算公允价值失败: {e}")
            return 0, 0

    def _determine_valuation_signal(self, fair_value: float, current_price: float,
                                  confidence: float) -> str:
        """确定估值信号"""
        try:
            deviation = (fair_value - current_price) / current_price

            # 根据置信度调整阈值
            if confidence >= 80:
                undervalued_threshold = -0.15  # 低估15%以上
                overvalued_threshold = 0.15   # 高估15%以上
            elif confidence >= 60:
                undervalued_threshold = -0.20  # 低估20%以上
                overvalued_threshold = 0.20   # 高估20%以上
            else:
                undervalued_threshold = -0.25  # 低估25%以上
                overvalued_threshold = 0.25   # 高估25%以上

            if deviation <= undervalued_threshold:
                return "显著低估"
            elif deviation <= -0.05:
                return "低估"
            elif deviation >= overvalued_threshold:
                return "显著高估"
            elif deviation >= 0.05:
                return "高估"
            else:
                return "合理估值"

        except Exception as e:
            logger.debug(f"确定估值信号失败: {e}")
            return "估值不确定"

    def _perform_sensitivity_analysis(self, financial_data: Any,
                                   base_params: DCFParameters) -> Dict[str, List[float]]:
        """执行敏感性分析"""
        try:
            sensitivity_results = {}

            # WACC敏感性
            wacc_variations = [base_params.wacc - 2, base_params.wacc, base_params.wacc + 2]
            wacc_values = []
            for wacc in wacc_variations:
                if wacc > 0:
                    modified_params = DCFParameters(
                        **{k: v for k, v in base_params.__dict__.items()},
                        wacc=wacc
                    )
                    dcf_result = self._perform_dcf_valuation(financial_data, modified_params)
                    wacc_values.append(dcf_result['value_per_share'])

            sensitivity_results['wacc'] = wacc_values

            # 增长率敏感性
            growth_variations = [
                base_params.revenue_growth_rate - 3,
                base_params.revenue_growth_rate,
                base_params.revenue_growth_rate + 3
            ]
            growth_values = []
            for growth in growth_variations:
                if growth >= 0:
                    modified_params = DCFParameters(
                        **{k: v for k, v in base_params.__dict__.items()},
                        revenue_growth_rate=growth
                    )
                    dcf_result = self._perform_dcf_valuation(financial_data, modified_params)
                    growth_values.append(dcf_result['value_per_share'])

            sensitivity_results['growth'] = growth_values

            # 利润率敏感性
            margin_variations = [
                base_params.operating_margin - 3,
                base_params.operating_margin,
                base_params.operating_margin + 3
            ]
            margin_values = []
            for margin in margin_variations:
                if margin >= 0:
                    modified_params = DCFParameters(
                        **{k: v for k, v in base_params.__dict__.items()},
                        operating_margin=margin
                    )
                    dcf_result = self._perform_dcf_valuation(financial_data, modified_params)
                    margin_values.append(dcf_result['value_per_share'])

            sensitivity_results['margin'] = margin_values

            return sensitivity_results

        except Exception as e:
            logger.error(f"敏感性分析失败: {e}")
            return {}

    def _extract_key_assumptions(self, dcf_params: DCFParameters,
                                 relative_result: Dict, financial_data: Any) -> List[str]:
        """提取关键假设"""
        try:
            assumptions = []

            # DCF假设
            assumptions.append(f"收入增长率假设: {dcf_params.revenue_growth_rate:.1f}%")
            assumptions.append(f"永续增长率假设: {dcf_params.terminal_growth_rate:.1f}%")
            assumptions.append(f"WACC假设: {dcf_params.wacc:.1f}%")
            assumptions.append(f"营业利润率假设: {dcf_params.operating_margin:.1f}%")

            # 相对估值假设
            industry_pe = relative_result.get('industry_pe', 0)
            current_pe = relative_result.get('current_pe', 0)
            if industry_pe > 0 and current_pe > 0:
                assumptions.append(f"行业PE倍数: {industry_pe:.1f}x")
                assumptions.append(f"当前PE倍数: {current_pe:.1f}x")

            # 风险因素
            if dcf_params.wacc > 12:
                assumptions.append("高风险溢价要求")

            if dcf_params.revenue_growth_rate > 20:
                assumptions.append("乐观增长假设")

            if dcf_params.debt_to_equity > 1.5:  # 如果存在这个属性
                assumptions.append("高财务杠杆风险")

            return assumptions

        except Exception as e:
            logger.debug(f"提取关键假设失败: {e}")
            return []

    def _calculate_value_range(self, fair_value: float, confidence: float,
                             sensitivity: Dict[str, List[float]]) -> Tuple[float, float]:
        """计算价值区间"""
        try:
            # 基于置信度调整区间宽度
            if confidence >= 80:
                range_factor = 0.15  # ±15%
            elif confidence >= 60:
                range_factor = 0.25  # ±25%
            else:
                range_factor = 0.40  # ±40%

            # 基于敏感性分析调整
            if 'wacc' in sensitivity and len(sensitivity['wacc']) >= 3:
                wacc_range = max(sensitivity['wacc']) - min(sensitivity['wacc'])
                if wacc_range > 0:
                    sensitivity_adjustment = wacc_range / fair_value
                    range_factor = max(range_factor, sensitivity_adjustment)

            lower_bound = fair_value * (1 - range_factor)
            upper_bound = fair_value * (1 + range_factor)

            return max(0, lower_bound), upper_bound

        except Exception as e:
            logger.debug(f"计算价值区间失败: {e}")
            return fair_value * 0.8, fair_value * 1.2

    def _get_latest_year(self, financial_data: Any) -> str:
        """获取最新年份"""
        try:
            years = list(financial_data.revenue.keys())
            if not years:
                raise InsufficientDataError('revenue', 1, 0)

            return str(max(int(year) for year in years))

        except Exception as e:
            logger.debug(f"获取最新年份失败: {e}")
            return "2024"  # 默认年份

    def _get_current_date(self) -> str:
        """获取当前日期"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d')