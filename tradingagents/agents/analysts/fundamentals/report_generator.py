"""
基本面分析报告生成器
生成专业的基本面分析报告，包含财务分析、估值结果和投资建议
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import logging
from datetime import datetime

from tradingagents.exceptions import (
    AnalysisError, ValidationError, handle_exceptions
)
from tradingagents.utils.logging_init import get_logger
from .data_collector import FinancialData
from .financial_analyzer import FinancialRatios, FinancialScore
from .valuation_model import ValuationResult

logger = get_logger(__name__)


@dataclass
class ReportSection:
    """报告段落"""
    title: str
    content: str
    importance: str  # high/medium/low
    data_points: List[Dict[str, Any]] = None


@dataclass
class FundamentalsReport:
    """基本面分析报告"""
    # 基本信息
    symbol: str
    company_name: str
    sector: str
    market: str
    analysis_date: str

    # 执行摘要
    executive_summary: str
    investment_recommendation: str  # 买入/持有/卖出
    confidence_level: float  # 置信度 0-100
    target_price: Optional[float]
    upside_potential: Optional[float]

    # 财务分析
    financial_highlights: List[str]
    profitability_analysis: str
    financial_health_analysis: str
    efficiency_analysis: str
    growth_analysis: str

    # 估值分析
    valuation_summary: str
    valuation_methodology: str
    valuation_signal: str
    fair_value_range: Tuple[float, float]

    # 风险分析
    key_risks: List[str]
    risk_factors: List[str]
    mitigating_factors: List[str]

    # 关键指标
    key_metrics: Dict[str, Any]
    financial_ratios: Dict[str, float]
    industry_comparison: Dict[str, str]

    # 结论和建议
    strengths: List[str]
    weaknesses: List[str]
    opportunities: List[str]
    threats: List[str]

    # 元数据
    report_quality_score: float
    data_quality_score: float
    analysis_depth: str  # deep/medium/basic


class FundamentalsReportGenerator:
    """基本面报告生成器"""

    def __init__(self):
        self.report_templates = self._load_report_templates()
        self.industry_insights = self._load_industry_insights()

    @handle_exceptions({
            Exception: AnalysisError
        })
    def generate_report(self, financial_data: FinancialData,
                       financial_ratios: FinancialRatios,
                       financial_score: FinancialScore,
                       valuation_result: ValuationResult,
                       market_info: Dict[str, Any]) -> FundamentalsReport:
        """
        生成基本面分析报告

        Args:
            financial_data: 财务数据
            financial_ratios: 财务比率
            financial_score: 财务评分
            valuation_result: 估值结果
            market_info: 市场信息

        Returns:
            FundamentalsReport: 完整的基本面分析报告

        Raises:
            AnalysisError: 报告生成失败
        """
        try:
            logger.info(f"📝 开始生成 {financial_data.symbol} 的基本面报告")

            # 1. 基本信息
            basic_info = self._generate_basic_info(financial_data, market_info)

            # 2. 执行摘要
            executive_summary = self._generate_executive_summary(
                financial_ratios, financial_score, valuation_result
            )

            # 3. 投资建议
            recommendation = self._generate_investment_recommendation(
                financial_score, valuation_result, financial_ratios
            )

            # 4. 财务分析
            financial_analysis = self._generate_financial_analysis(
                financial_data, financial_ratios, financial_score
            )

            # 5. 估值分析
            valuation_analysis = self._generate_valuation_analysis(
                valuation_result, financial_ratios
            )

            # 6. 风险分析
            risk_analysis = self._generate_risk_analysis(
                financial_ratios, financial_score, valuation_result
            )

            # 7. SWOT分析
            swot_analysis = self._generate_swot_analysis(
                financial_score, valuation_result, financial_ratios
            )

            # 8. 关键指标
            key_metrics = self._generate_key_metrics(
                financial_data, financial_ratios, valuation_result
            )

            # 9. 报告质量评估
            report_quality = self._assess_report_quality(
                financial_data, financial_ratios, financial_score, valuation_result
            )

            # 10. 生成完整报告
            report = FundamentalsReport(
                symbol=financial_data.symbol,
                company_name=financial_data.company_name,
                sector=financial_data.sector,
                market=financial_data.market,
                analysis_date=datetime.now().strftime('%Y-%m-%d'),
                executive_summary=executive_summary,
                investment_recommendation=recommendation['action'],
                confidence_level=recommendation['confidence'],
                target_price=valuation_result.fair_value,
                upside_potential=valuation_result.upside_potential,
                financial_highlights=financial_analysis['highlights'],
                profitability_analysis=financial_analysis['profitability'],
                financial_health_analysis=financial_analysis['financial_health'],
                efficiency_analysis=financial_analysis['efficiency'],
                growth_analysis=financial_analysis['growth'],
                valuation_summary=valuation_analysis['summary'],
                valuation_methodology=valuation_analysis['methodology'],
                valuation_signal=valuation_result.valuation_signal,
                fair_value_range=valuation_result.fair_value_range,
                key_risks=risk_analysis['key_risks'],
                risk_factors=risk_analysis['risk_factors'],
                mitigating_factors=risk_analysis['mitigations'],
                key_metrics=key_metrics['metrics'],
                financial_ratios=self._format_financial_ratios(financial_ratios),
                industry_comparison=self._generate_industry_comparison(financial_score),
                strengths=swot_analysis['strengths'],
                weaknesses=swot_analysis['weaknesses'],
                opportunities=swot_analysis['opportunities'],
                threats=swot_analysis['threats'],
                report_quality_score=report_quality['overall'],
                data_quality_score=report_quality['data_quality'],
                analysis_depth=report_quality['depth']
            )

            logger.info(f"✅ {financial_data.symbol} 基本面报告生成完成")
            return report

        except Exception as e:
            logger.error(f"❌ {financial_data.symbol} 报告生成失败: {e}")
            raise AnalysisError(f"报告生成失败: {e}", 'REPORT_GENERATION_FAILED')

    def _generate_basic_info(self, financial_data: FinancialData,
                            market_info: Dict[str, Any]) -> Dict[str, Any]:
        """生成基本信息"""
        return {
            'symbol': financial_data.symbol,
            'company_name': financial_data.company_name,
            'sector': financial_data.sector,
            'market': financial_data.market,
            'currency': financial_data.data_currency,
            'fiscal_year_end': financial_data.fiscal_year_end
        }

    def _generate_executive_summary(self, financial_ratios: FinancialRatios,
                                  financial_score: FinancialScore,
                                  valuation_result: ValuationResult) -> str:
        """生成执行摘要"""
        try:
            # 关键财务表现
            profitability_desc = self._describe_profitability(financial_ratios)
            financial_health_desc = self._describe_financial_health(financial_ratios)
            growth_desc = self._describe_growth(financial_ratios)

            # 估值情况
            valuation_desc = self._describe_valuation(valuation_result)

            # 综合评价
            overall_assessment = self._generate_overall_assessment(
                financial_score.overall_score, valuation_result.valuation_signal
            )

            summary = f"""
## 执行摘要

**财务表现**: {profitability_desc}公司盈利能力{financial_ratios.roe:.1f}%的净资产收益率和{financial_ratios.net_margin:.1f}%的净利率。

**财务健康**: {financial_health_desc}债务权益比为{financial_ratios.debt_to_equity:.2f}，财务结构{self._assess_financial_structure(financial_ratios.debt_to_equity)}。

**成长性**: {growth_desc}收入增长率为{financial_ratios.revenue_growth:.1f}%，盈利增长率为{financial_ratios.earnings_growth:.1f}%。

**估值评估**: {valuation_desc}当前估值信号为{valuation_result.valuation_signal}。

**综合评价**: {overall_assessment}
            """.strip()

            return summary

        except Exception as e:
            logger.error(f"生成执行摘要失败: {e}")
            return "执行摘要生成失败，请查看详细分析部分。"

    def _generate_investment_recommendation(self, financial_score: FinancialScore,
                                        valuation_result: ValuationResult,
                                        financial_ratios: FinancialRatios) -> Dict[str, Any]:
        """生成投资建议"""
        try:
            # 基于财务评分的建议
            financial_signal = self._interpret_financial_score(financial_score.overall_score)

            # 基于估值的建议
            valuation_signal = valuation_result.valuation_signal

            # 综合决策逻辑
            action, confidence = self._make_investment_decision(
                financial_signal, valuation_signal, financial_score.overall_score,
                valuation_result.confidence_level
            )

            # 生成建议理由
            reasoning = self._generate_recommendation_reasoning(
                action, financial_score, valuation_result, financial_ratios
            )

            # 价格目标
            target_price = valuation_result.fair_value
            price_range = valuation_result.fair_value_range

            return {
                'action': action,
                'confidence': confidence,
                'reasoning': reasoning,
                'target_price': target_price,
                'price_range': price_range,
                'holding_period': self._suggest_holding_period(action, financial_ratios),
                'risk_level': self._assess_risk_level(financial_ratios, financial_score)
            }

        except Exception as e:
            logger.error(f"生成投资建议失败: {e}")
            return {
                'action': '持有',
                'confidence': 50.0,
                'reasoning': '由于数据不足，暂时建议持有',
                'target_price': None,
                'price_range': (0, 0),
                'holding_period': '待定',
                'risk_level': '中等'
            }

    def _generate_financial_analysis(self, financial_data: FinancialData,
                                   financial_ratios: FinancialRatios,
                                   financial_score: FinancialScore) -> Dict[str, str]:
        """生成财务分析"""
        try:
            # 财务亮点
            highlights = self._extract_financial_highlights(financial_ratios, financial_score)

            # 盈利能力分析
            profitability = self._analyze_profitability_detailed(financial_ratios, financial_score)

            # 财务健康分析
            financial_health = self._analyze_financial_health_detailed(financial_ratios, financial_score)

            # 运营效率分析
            efficiency = self._analyze_efficiency_detailed(financial_ratios, financial_score)

            # 成长性分析
            growth = self._analyze_growth_detailed(financial_ratios, financial_score)

            return {
                'highlights': highlights,
                'profitability': profitability,
                'financial_health': financial_health,
                'efficiency': efficiency,
                'growth': growth
            }

        except Exception as e:
            logger.error(f"生成财务分析失败: {e}")
            return {
                'highlights': [],
                'profitability': '盈利能力分析失败',
                'financial_health': '财务健康分析失败',
                'efficiency': '运营效率分析失败',
                'growth': '成长性分析失败'
            }

    def _generate_valuation_analysis(self, valuation_result: ValuationResult,
                                   financial_ratios: FinancialRatios) -> Dict[str, str]:
        """生成估值分析"""
        try:
            # 估值摘要
            summary = f"""
基于多种估值方法的综合分析，{valuation_result.valuation_signal}。
DCF估值为{valuation_result.dcf_value_per_share:.2f}，相对估值为{valuation_result.relative_value:.2f}，
资产基础估值为{valuation_result.asset_value:.2f}。

公允价值为{valuation_result.fair_value:.2f}，相比当前价格{valuation_result.current_price:.2f}
{'上升' if valuation_result.upside_potential > 0 else '下降'}{abs(valuation_result.upside_potential):.1f}%。
            """.strip()

            # 估值方法说明
            methodology = f"""
**DCF估值**: 基于现金流折现模型，考虑了未来5年的高增长期和5年的过渡期，
永续增长率为3%，加权平均资本成本(WACC)为10%。

**相对估值**: 基于行业可比公司估值倍数，综合考虑了PE、PB、PS和EV/EBITDA等指标。

**资产基础估值**: 基于公司资产负债表，考虑了资产质量和无形资产价值。

**综合估值**: 采用加权平均方法，DCF权重50%，相对估值权重35%，资产估值权重15%。
            """.strip()

            # 敏感性分析说明
            sensitivity_desc = self._describe_sensitivity_analysis(valuation_result)

            return {
                'summary': summary,
                'methodology': methodology,
                'sensitivity': sensitivity_desc
            }

        except Exception as e:
            logger.error(f"生成估值分析失败: {e}")
            return {
                'summary': '估值分析失败',
                'methodology': '估值方法说明失败',
                'sensitivity': '敏感性分析失败'
            }

    def _generate_risk_analysis(self, financial_ratios: FinancialRatios,
                                financial_score: FinancialScore,
                                valuation_result: ValuationResult) -> Dict[str, List[str]]:
        """生成风险分析"""
        try:
            key_risks = []
            risk_factors = []
            mitigating_factors = []

            # 财务风险
            if financial_ratios.debt_to_equity > 2.0:
                key_risks.append("高财务杠杆风险")
                risk_factors.append(f"债务权益比过高({financial_ratios.debt_to_equity:.2f})")
            else:
                mitigating_factors.append("财务杠杆适中")

            if financial_ratios.interest_coverage < 2:
                key_risks.append("利息保障不足风险")
                risk_factors.append(f"利息保障倍数偏低({financial_ratios.interest_coverage:.1f})")
            else:
                mitigating_factors.append("利息保障充足")

            # 盈利能力风险
            if financial_ratios.roe < 5:
                key_risks.append("盈利能力不足风险")
                risk_factors.append(f"净资产收益率偏低({financial_ratios.roe:.1f}%)")
            elif financial_ratios.roe > 20:
                risk_factors.append("高ROE可能不可持续")
            else:
                mitigating_factors.append("盈利能力良好")

            # 成长性风险
            if financial_ratios.revenue_growth < 0:
                key_risks.append("收入下滑风险")
                risk_factors.append(f"收入负增长({financial_ratios.revenue_growth:.1f}%)")
            elif financial_ratios.revenue_growth > 30:
                risk_factors.append("高增长可能不可持续")
            else:
                mitigating_factors.append("增长稳健")

            # 估值风险
            if valuation_result.valuation_signal in ["显著高估", "高估"]:
                key_risks.append("估值回调风险")
                risk_factors.append(f"估值偏高，上行潜力{valuation_result.upside_potential:.1f}%")
            elif valuation_result.confidence_level < 50:
                key_risks.append("估值不确定性风险")
                risk_factors.append("估值置信度较低")
            else:
                mitigating_factors.append("估值合理")

            # 现金流风险
            if financial_ratios.operating_cash_flow_ratio < 0.8:
                key_risks.append("现金流风险")
                risk_factors.append(f"经营现金流比率偏低({financial_ratios.operating_cash_flow_ratio:.1f})")
            else:
                mitigating_factors.append("现金流良好")

            # 行业特定风险
            industry_risks = self._assess_industry_specific_risks(financial_ratios)
            risk_factors.extend(industry_risks)

            return {
                'key_risks': key_risks,
                'risk_factors': risk_factors,
                'mitigations': mitigating_factors
            }

        except Exception as e:
            logger.error(f"生成风险分析失败: {e}")
            return {
                'key_risks': ['风险分析失败'],
                'risk_factors': ['无法评估风险因素'],
                'mitigations': ['无法识别风险缓解因素']
            }

    def _generate_swot_analysis(self, financial_score: FinancialScore,
                               valuation_result: ValuationResult,
                               financial_ratios: FinancialRatios) -> Dict[str, List[str]]:
        """生成SWOT分析"""
        try:
            # 优势 (Strengths)
            strengths = financial_score.strengths.copy()

            # 劣势 (Weaknesses)
            weaknesses = financial_score.weaknesses.copy()

            # 机会 (Opportunities)
            opportunities = self._identify_opportunities(financial_ratios, valuation_result)

            # 威胁 (Threats)
            threats = self._identify_threats(financial_ratios, valuation_result)

            return {
                'strengths': strengths,
                'weaknesses': weaknesses,
                'opportunities': opportunities,
                'threats': threats
            }

        except Exception as e:
            logger.error(f"生成SWOT分析失败: {e}")
            return {
                'strengths': ['优势分析失败'],
                'weaknesses': ['劣势分析失败'],
                'opportunities': ['机会分析失败'],
                'threats': ['威胁分析失败']
            }

    def _generate_key_metrics(self, financial_data: FinancialData,
                             financial_ratios: FinancialRatios,
                             valuation_result: ValuationResult) -> Dict[str, Any]:
        """生成关键指标"""
        try:
            latest_year = self._get_latest_year(financial_data)

            metrics = {
                # 基本财务数据
                'revenue': financial_data.revenue.get(latest_year, 0),
                'net_income': financial_data.net_income.get(latest_year, 0),
                'total_assets': financial_data.total_assets.get(latest_year, 0),
                'shareholders_equity': financial_data.shareholders_equity.get(latest_year, 0),
                'total_debt': financial_data.total_debt.get(latest_year, 0),

                # 关键比率
                'roe': financial_ratios.roe,
                'roa': financial_ratios.roa,
                'net_margin': financial_ratios.net_margin,
                'gross_margin': financial_ratios.gross_margin,
                'debt_to_equity': financial_ratios.debt_to_equity,
                'pe_ratio': financial_ratios.pe_ratio,
                'pb_ratio': financial_ratios.pb_ratio,

                # 估值数据
                'current_price': valuation_result.current_price,
                'fair_value': valuation_result.fair_value,
                'upside_potential': valuation_result.upside_potential,

                # 成长数据
                'revenue_growth': financial_ratios.revenue_growth,
                'earnings_growth': financial_ratios.earnings_growth,

                # 效率数据
                'asset_turnover': financial_ratios.asset_turnover,
                'inventory_turnover': financial_ratios.inventory_turnover,
                'receivables_turnover': financial_ratios.receivables_turnover,

                # 现金流数据
                'operating_cash_flow_ratio': financial_ratios.operating_cash_flow_ratio,
                'free_cash_flow_ratio': financial_ratios.free_cash_flow_ratio
            }

            return {
                'metrics': metrics,
                'metric_explanations': self._generate_metric_explanations(metrics)
            }

        except Exception as e:
            logger.error(f"生成关键指标失败: {e}")
            return {
                'metrics': {},
                'metric_explanations': {}
            }

    def _assess_report_quality(self, financial_data: FinancialData,
                               financial_ratios: FinancialRatios,
                               financial_score: FinancialScore,
                               valuation_result: ValuationResult) -> Dict[str, Any]:
        """评估报告质量"""
        try:
            # 数据完整性评分
            data_quality = self._assess_data_quality(financial_data)

            # 分析一致性评分
            consistency_score = self._assess_analysis_consistency(
                financial_score, valuation_result
            )

            # 估值置信度
            valuation_confidence = valuation_result.confidence_level

            # 综合质量评分
            overall_quality = (
                data_quality * 0.3 +
                consistency_score * 0.3 +
                valuation_confidence * 0.4
            )

            # 分析深度
            depth = self._determine_analysis_depth(data_quality, overall_quality)

            return {
                'overall': overall_quality,
                'data_quality': data_quality,
                'consistency': consistency_score,
                'depth': depth
            }

        except Exception as e:
            logger.error(f"评估报告质量失败: {e}")
            return {
                'overall': 50.0,
                'data_quality': 50.0,
                'consistency': 50.0,
                'depth': 'basic'
            }

    def _format_financial_ratios(self, ratios: FinancialRatios) -> Dict[str, float]:
        """格式化财务比率"""
        return {
            '净资产收益率': ratios.roe,
            '总资产收益率': ratios.roa,
            '净利率': ratios.net_margin,
            '毛利率': ratios.gross_margin,
            '营业利润率': ratios.operating_margin,
            '债务权益比': ratios.debt_to_equity,
            '资产负债率': ratios.debt_to_assets,
            '利息保障倍数': ratios.interest_coverage,
            '资产周转率': ratios.asset_turnover,
            '存货周转率': ratios.inventory_turnover,
            '应收账款周转率': ratios.receivables_turnover,
            '收入增长率': ratios.revenue_growth,
            '盈利增长率': ratios.earnings_growth,
            '市盈率': ratios.pe_ratio,
            '市净率': ratios.pb_ratio,
            '市销率': ratios.ps_ratio,
            '经营现金流比率': ratios.operating_cash_flow_ratio,
            '自由现金流比率': ratios.free_cash_flow_ratio
        }

    def _generate_industry_comparison(self, financial_score: FinancialScore) -> Dict[str, str]:
        """生成行业对比"""
        try:
            comparison = {}

            for metric, comparison_pct in financial_score.industry_comparison.items():
                if comparison_pct > 10:
                    comparison[metric] = "显著优于行业平均"
                elif comparison_pct > 0:
                    comparison[metric] = "优于行业平均"
                elif comparison_pct > -10:
                    comparison[metric] = "略低于行业平均"
                else:
                    comparison[metric] = "显著低于行业平均"

            return comparison

        except Exception as e:
            logger.error(f"生成行业对比失败: {e}")
            return {}

    # 辅助方法
    def _describe_profitability(self, ratios: FinancialRatios) -> str:
        """描述盈利能力"""
        if ratios.roe >= 15:
            return "优秀"
        elif ratios.roe >= 10:
            return "良好"
        elif ratios.roe >= 5:
            return "一般"
        else:
            return "较差"

    def _describe_financial_health(self, ratios: FinancialRatios) -> str:
        """描述财务健康"""
        if ratios.debt_to_equity <= 0.5:
            return "财务结构稳健，"
        elif ratios.debt_to_equity <= 1.0:
            return "财务结构适中，"
        elif ratios.debt_to_equity <= 2.0:
            return "财务杠杆偏高，"
        else:
            return "财务风险较高，"

    def _describe_growth(self, ratios: FinancialRatios) -> str:
        """描述成长性"""
        if ratios.revenue_growth >= 20:
            return "收入增长强劲，"
        elif ratios.revenue_growth >= 10:
            return "收入增长良好，"
        elif ratios.revenue_growth >= 0:
            return "收入增长平稳，"
        else:
            return "收入出现下滑，"

    def _describe_valuation(self, valuation_result: ValuationResult) -> str:
        """描述估值情况"""
        if valuation_result.valuation_signal == "显著低估":
            return "当前估值显著偏低，具备较大投资价值。"
        elif valuation_result.valuation_signal == "低估":
            return "当前估值偏低，具备投资价值。"
        elif valuation_result.valuation_signal == "合理估值":
            return "当前估值处于合理区间。"
        elif valuation_result.valuation_signal == "高估":
            return "当前估值偏高，需要谨慎。"
        elif valuation_result.valuation_signal == "显著高估":
            return "当前估值显著偏高，投资风险较大。"
        else:
            return "估值不确定性较高。"

    def _generate_overall_assessment(self, financial_score: float,
                                    valuation_signal: str) -> str:
        """生成综合评价"""
        if financial_score >= 80 and "低估" in valuation_signal:
            return "公司基本面优秀，估值合理偏低，具备较好的投资价值。"
        elif financial_score >= 60 and "合理估值" in valuation_signal:
            return "公司基本面良好，估值合理，可考虑中长期投资。"
        elif financial_score >= 40:
            return "公司基本面一般，需要结合行业前景和公司转型策略进行评估。"
        else:
            return "公司基本面存在一定问题，建议谨慎投资或等待基本面改善。"

    def _assess_financial_structure(self, debt_to_equity: float) -> str:
        """评估财务结构"""
        if debt_to_equity <= 0.5:
            return "稳健"
        elif debt_to_equity <= 1.0:
            return "适中"
        elif debt_to_equity <= 2.0:
            return "偏高"
        else:
            return "风险较高"

    def _interpret_financial_score(self, score: float) -> str:
        """解释财务评分"""
        if score >= 80:
            return "优秀"
        elif score >= 60:
            return "良好"
        elif score >= 40:
            return "一般"
        else:
            return "较差"

    def _make_investment_decision(self, financial_signal: str, valuation_signal: str,
                               financial_score: float, valuation_confidence: float) -> Tuple[str, float]:
        """制定投资决策"""
        # 决策矩阵
        if financial_signal in ["优秀", "良好"] and "低估" in valuation_signal:
            return "买入", min(95, (financial_score + valuation_confidence) / 2)
        elif financial_signal in ["优秀", "良好"] and "合理估值" in valuation_signal:
            return "持有", min(85, (financial_score + valuation_confidence) / 2)
        elif financial_signal in ["一般"] and "低估" in valuation_signal:
            return "持有", min(75, (financial_score + valuation_confidence) / 2)
        elif "较差" in financial_signal or "高估" in valuation_signal:
            return "卖出", max(25, (financial_score + valuation_confidence) / 2)
        else:
            return "持有", 50.0

    def _suggest_holding_period(self, action: str, ratios: FinancialRatios) -> str:
        """建议持有期"""
        if action == "买入":
            if ratios.revenue_growth >= 15:
                return "长期投资(2-3年)"
            else:
                return "中期投资(1-2年)"
        elif action == "持有":
            return "短期观察(3-6个月)"
        else:
            return "建议减持或退出"

    def _assess_risk_level(self, ratios: FinancialRatios, score: FinancialScore) -> str:
        """评估风险等级"""
        risk_factors = 0

        if ratios.debt_to_equity > 2.0:
            risk_factors += 1
        if ratios.roe < 5:
            risk_factors += 1
        if ratios.revenue_growth < 0:
            risk_factors += 1
        if ratios.interest_coverage < 2:
            risk_factors += 1

        if risk_factors >= 3:
            return "高风险"
        elif risk_factors >= 2:
            return "中等风险"
        elif risk_factors >= 1:
            return "中低风险"
        else:
            return "低风险"

    def _get_latest_year(self, financial_data: FinancialData) -> str:
        """获取最新年份"""
        years = list(financial_data.revenue.keys())
        return str(max(int(year) for year in years)) if years else "2024"

    def _load_report_templates(self) -> Dict[str, str]:
        """加载报告模板"""
        return {
            'executive_summary': """
# {company_name} ({symbol}) 基本面分析报告

## 执行摘要
{summary}
            """,
            'financial_analysis': """
## 财务分析

### 盈利能力分析
{profitability_analysis}

### 财务健康分析
{financial_health_analysis}

### 运营效率分析
{efficiency_analysis}

### 成长性分析
{growth_analysis}
            """,
            'valuation_analysis': """
## 估值分析

### 估值摘要
{valuation_summary}

### 估值方法说明
{valuation_methodology}

### 敏感性分析
{sensitivity_analysis}
            """,
            'risk_analysis': """
## 风险分析

### 主要风险
{key_risks}

### 风险因素
{risk_factors}

### 风险缓解因素
{mitigating_factors}
            """
        }

    def _load_industry_insights(self) -> Dict[str, Dict[str, Any]]:
        """加载行业洞察"""
        return {
            'technology': {
                'key_drivers': ['技术创新', '市场需求增长', '数字化转型'],
                'risks': ['技术迭代快', '竞争激烈', '政策监管'],
                'opportunities': ['AI应用', '云计算', '5G建设']
            },
            'finance': {
                'key_drivers': ['利率环境', '经济增长', '金融创新'],
                'risks': ['信用风险', '利率风险', '监管变化'],
                'opportunities': ['数字银行', '绿色金融', '财富管理']
            },
            'healthcare': {
                'key_drivers': ['人口老龄化', '医疗技术进步', '健康意识提升'],
                'risks': ['政策风险', '研发风险', '竞争风险'],
                'opportunities': ['生物技术', '数字医疗', '预防医学']
            }
        }