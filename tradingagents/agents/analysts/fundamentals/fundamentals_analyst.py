"""
基本面分析师 - 重构版本
使用模块化架构，职责分离，提高代码可维护性
"""

from typing import Dict, List, Any, Optional
import logging
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage

from tradingagents.exceptions import (
    AnalysisError, DataFetchError, handle_exceptions
)
from tradingagents.utils.logging_init import get_logger
from tradingagents.utils.tool_logging import log_analyst_module
from tradingagents.agents.utils.google_tool_handler import GoogleToolCallHandler

# 导入重构后的模块
from .data_collector import FundamentalsDataCollector
from .financial_analyzer import FinancialAnalyzer, FinancialRatios, FinancialScore
from .valuation_model import ValuationModel, ValuationResult, DCFParameters
from .report_generator import FundamentalsReportGenerator, FundamentalsReport

logger = get_logger(__name__)


class FundamentalsAnalyst:
    """基本面分析师 - 重构版本"""

    def __init__(self, llm, toolkit, config: Optional[Dict[str, Any]] = None):
        """
        初始化基本面分析师

        Args:
            llm: 语言模型
            toolkit: 工具包
            config: 配置参数
        """
        self.llm = llm
        self.toolkit = toolkit
        self.config = config or {}

        # 初始化组件
        self.data_collector = FundamentalsDataCollector(
            enable_cache=self.config.get('enable_cache', True)
        )
        self.financial_analyzer = FinancialAnalyzer(
            industry_benchmarks=self.config.get('industry_benchmarks')
        )
        self.valuation_model = ValuationModel()
        self.report_generator = FundamentalsReportGenerator()

        # 初始化提示模板
        self.prompt = self._create_prompt_template()

        logger.debug("📊 基本面分析师初始化完成")

    def _create_prompt_template(self) -> ChatPromptTemplate:
        """创建基本面分析提示模板"""
        system_prompt = """你是一位专业的股票基本面分析师，具备以下核心能力：

## 分析框架
1. **财务数据收集**: 从多个可靠数据源收集完整的财务信息
2. **财务比率分析**: 计算并分析关键财务比率和指标
3. **估值模型应用**: 使用DCF、相对估值等多种估值方法
4. **风险评估**: 识别和评估财务风险和投资风险
5. **投资建议**: 基于全面分析给出明确的投资建议

## 分析要点
- **盈利能力**: ROE、ROA、净利率、毛利率等关键指标
- **财务健康**: 债务结构、偿债能力、现金流状况
- **运营效率**: 资产周转率、存货周转率、应收账款周转率
- **成长性**: 收入增长、盈利增长、可持续性分析
- **估值合理性**: PE、PB、PS等估值倍数的合理性评估

## 报告要求
- 数据来源可靠，分析逻辑清晰
- 关键假设明确，敏感性分析完整
- 风险提示充分，投资建议具体
- 语言专业但不晦涩，便于投资者理解

请基于提供的财务数据和市场信息，进行全面深入的基本面分析。"""

        return ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
            ("human", """请分析股票 {symbol} 在 {date} 的基本面情况。

## 已有信息
- 公司信息: {company_info}
- 市场信息: {market_info}
- 财务数据: {financial_data}
- 分析师团队: {analyst_team}
- 财务比率: {financial_ratios}
- 财务评分: {financial_score}
- 估值结果: {valuation_result}

## 分析任务
1. 验证和补充财务数据分析
2. 评估公司盈利能力和财务健康度
3. 分析行业竞争地位和发展前景
4. 进行综合估值和风险评估
5. 提供明确的投资建议和理由

请提供详细的基本面分析报告，包含关键财务指标、估值结论和投资建议。""")
        ])

    @log_analyst_module("fundamentals")
    @handle_exceptions({
            DataFetchError: AnalysisError,
            Exception: AnalysisError
        })
    def analyze_fundamentals(self, state: Dict[str, Any]) -> AIMessage:
        """
        执行基本面分析

        Args:
            state: 分析状态，包含股票信息、日期等

        Returns:
            AIMessage: 基本面分析结果

        Raises:
            AnalysisError: 分析过程失败
        """
        try:
            logger.debug(f"📊 ===== 基本面分析师节点开始 =====")

            # 1. 提取基本参数
            symbol = state["company_of_interest"]
            analysis_date = state["trade_date"]
            market_info = state.get("market_info", {})
            messages = state.get("messages", [])

            logger.debug(f"📊 分析参数: symbol={symbol}, date={analysis_date}")
            logger.debug(f"📊 现有消息数量: {len(messages)}")

            # 2. 收集财务数据
            logger.debug(f"📊 开始收集 {symbol} 的财务数据")
            financial_data = self.data_collector.collect_financial_data(
                symbol, market_info, years=3
            )

            # 3. 进行财务分析
            logger.debug(f"📊 开始财务比率分析")
            financial_ratios, financial_score = self.financial_analyzer.analyze_financials(
                financial_data
            )

            # 4. 进行估值分析
            logger.debug(f"📊 开始估值分析")
            current_price = self._get_current_price(symbol, market_info)
            shares_outstanding = self._get_shares_outstanding(symbol, financial_data)

            # 获取自定义DCF参数（如果有）
            dcf_params = self._get_dcf_parameters(symbol, market_info)

            valuation_result = self.valuation_model.value_company(
                financial_data=financial_data,
                current_price=current_price,
                shares_outstanding=shares_outstanding,
                industry=financial_data.sector,
                custom_dcf_params=dcf_params
            )

            # 5. 生成分析报告
            logger.debug(f"📊 生成基本面分析报告")
            report = self.report_generator.generate_report(
                financial_data=financial_data,
                financial_ratios=financial_ratios,
                financial_score=financial_score,
                valuation_result=valuation_result,
                market_info=market_info
            )

            # 6. 格式化分析结果
            formatted_result = self._format_analysis_result(
                symbol, analysis_date, report, financial_data,
                financial_ratios, financial_score, valuation_result
            )

            # 7. 构建AI消息响应
            response_message = self._build_response_message(
                symbol, analysis_date, formatted_result, report
            )

            logger.debug(f"📊 ===== 基本面分析师节点完成 =====")
            return response_message

        except Exception as e:
            logger.error(f"❌ 基本面分析失败: {e}")
            error_message = f"基本面分析过程出现错误: {str(e)}"
            return AIMessage(content=error_message)

    def _get_current_price(self, symbol: str, market_info: Dict[str, Any]) -> float:
        """获取当前股价"""
        try:
            # 尝试从统一接口获取实时价格
            from tradingagents.dataflows.interface import get_stock_price_unified
            price_data = get_stock_price_unified(symbol)

            if price_data and 'current' in price_data:
                return float(price_data['current'])

            # 降级方案：使用默认价格
            logger.warning(f"无法获取 {symbol} 实时价格，使用默认值")
            return 100.0  # 默认价格

        except Exception as e:
            logger.warning(f"获取 {symbol} 价格失败: {e}")
            return 100.0

    def _get_shares_outstanding(self, symbol: str, financial_data: Any) -> float:
        """获取流通股数"""
        try:
            # 尝试从财务数据获取
            if hasattr(financial_data, 'shares_outstanding'):
                return financial_data.shares_outstanding

            # 使用默认值 (实际应该从数据源获取)
            logger.warning(f"无法获取 {symbol} 股数，使用默认值")
            return 1000000000  # 10亿股

        except Exception as e:
            logger.warning(f"获取 {symbol} 股数失败: {e}")
            return 1000000000

    def _get_dcf_parameters(self, symbol: str, market_info: Dict[str, Any]) -> Optional[DCFParameters]:
        """获取自定义DCF参数"""
        try:
            # 从配置中获取特定股票的DCF参数
            stock_params = self.config.get('stock_dcf_params', {})
            if symbol in stock_params:
                params = stock_params[symbol]
                return DCFParameters(**params)

            # 根据市场获取默认参数
            market_params = self.config.get('market_dcf_params', {})
            if market_info.get('is_china') and 'china' in market_params:
                params = market_params['china']
                return DCFParameters(**params)

            return None  # 使用默认参数

        except Exception as e:
            logger.warning(f"获取DCF参数失败: {e}")
            return None

    def _format_analysis_result(self, symbol: str, analysis_date: str,
                               report: FundamentalsReport, financial_data: Any,
                               financial_ratios: FinancialRatios,
                               financial_score: FinancialScore,
                               valuation_result: ValuationResult) -> Dict[str, Any]:
        """格式化分析结果"""
        try:
            # 基本信息
            basic_info = {
                'symbol': symbol,
                'company_name': report.company_name,
                'sector': report.sector,
                'market': report.market,
                'analysis_date': analysis_date
            }

            # 投资建议
            investment_recommendation = {
                'action': report.investment_recommendation,
                'confidence': report.confidence_level,
                'target_price': report.target_price,
                'upside_potential': report.upside_potential,
                'risk_level': self._assess_risk_level(financial_ratios)
            }

            # 财务亮点
            financial_highlights = {
                'roe': financial_ratios.roe,
                'net_margin': financial_ratios.net_margin,
                'revenue_growth': financial_ratios.revenue_growth,
                'debt_to_equity': financial_ratios.debt_to_equity,
                'financial_score': financial_score.overall_score
            }

            # 估值分析
            valuation_analysis = {
                'fair_value': valuation_result.fair_value,
                'valuation_signal': valuation_result.valuation_signal,
                'dcf_value': valuation_result.dcf_value_per_share,
                'relative_value': valuation_result.relative_value,
                'asset_value': valuation_result.asset_value,
                'confidence': valuation_result.confidence_level
            }

            # 风险评估
            risk_assessment = {
                'key_risks': report.key_risks,
                'risk_factors': report.risk_factors,
                'mitigating_factors': report.mitigating_factors
            }

            return {
                'basic_info': basic_info,
                'investment_recommendation': investment_recommendation,
                'financial_highlights': financial_highlights,
                'valuation_analysis': valuation_analysis,
                'risk_assessment': risk_assessment,
                'full_report': report
            }

        except Exception as e:
            logger.error(f"格式化分析结果失败: {e}")
            return {}

    def _build_response_message(self, symbol: str, analysis_date: str,
                               formatted_result: Dict[str, Any],
                               report: FundamentalsReport) -> AIMessage:
        """构建响应消息"""
        try:
            if not formatted_result:
                return AIMessage(content="基本面分析结果格式化失败")

            # 生成简洁的分析摘要
            content = f"""
## 📊 {symbol} 基本面分析报告

### 🎯 投资建议
**建议**: {formatted_result['investment_recommendation']['action']}
**置信度**: {formatted_result['investment_recommendation']['confidence']:.1f}%
**目标价格**: {formatted_result['investment_recommendation']['target_price']:.2f}
**上行潜力**: {formatted_result['investment_recommendation']['upside_potential']:.1f}%
**风险等级**: {formatted_result['investment_recommendation']['risk_level']}

### 📈 财务亮点
- **净资产收益率**: {formatted_result['financial_highlights']['roe']:.1f}%
- **净利率**: {formatted_result['financial_highlights']['net_margin']:.1f}%
- **收入增长**: {formatted_result['financial_highlights']['revenue_growth']:.1f}%
- **债务权益比**: {formatted_result['financial_highlights']['debt_to_equity']:.2f}
- **财务评分**: {formatted_result['financial_highlights']['financial_score']:.1f}/100

### 💰 估值分析
- **公允价值**: {formatted_result['valuation_analysis']['fair_value']:.2f}
- **估值信号**: {formatted_result['valuation_analysis']['valuation_signal']}
- **DCF估值**: {formatted_result['valuation_analysis']['dcf_value']:.2f}
- **相对估值**: {formatted_result['valuation_analysis']['relative_value']:.2f}
- **置信度**: {formatted_result['valuation_analysis']['confidence']:.1f}%

### ⚠️ 主要风险
{chr(10).join(f"- {risk}" for risk in formatted_result['risk_assessment']['key_risks'][:5])}

### 📋 执行摘要
{report.executive_summary}

---
*分析日期: {analysis_date}*
*数据质量评分: {report.data_quality_score:.1f}/100*
*报告质量评分: {report.report_quality_score:.1f}/100*
            """.strip()

            return AIMessage(content=content)

        except Exception as e:
            logger.error(f"构建响应消息失败: {e}")
            return AIMessage(content="基本面分析报告生成失败")

    def _assess_risk_level(self, ratios: FinancialRatios) -> str:
        """评估风险等级"""
        risk_score = 0

        # 债务风险评估
        if ratios.debt_to_equity > 2.0:
            risk_score += 2
        elif ratios.debt_to_equity > 1.0:
            risk_score += 1

        # 盈利能力风险评估
        if ratios.roe < 5:
            risk_score += 2
        elif ratios.roe < 10:
            risk_score += 1

        # 成长性风险评估
        if ratios.revenue_growth < 0:
            risk_score += 2
        elif ratios.revenue_growth < 5:
            risk_score += 1

        # 利息保障风险评估
        if ratios.interest_coverage < 2:
            risk_score += 2
        elif ratios.interest_coverage < 4:
            risk_score += 1

        # 现金流风险评估
        if ratios.operating_cash_flow_ratio < 0.8:
            risk_score += 1

        # 风险等级判定
        if risk_score >= 6:
            return "高风险"
        elif risk_score >= 4:
            return "中高风险"
        elif risk_score >= 2:
            return "中等风险"
        else:
            return "低风险"


def create_fundamentals_analyst(llm, toolkit):
    """
    创建基本面分析师节点函数

    Args:
        llm: 语言模型
        toolkit: 工具包

    Returns:
        基本面分析师节点函数
    """
    analyst = FundamentalsAnalyst(llm, toolkit)

    def fundamentals_analyst_node(state):
        """基本面分析师节点"""
        return analyst.analyze_fundamentals(state)

    return fundamentals_analyst_node