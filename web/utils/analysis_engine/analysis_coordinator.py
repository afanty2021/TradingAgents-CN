"""
分析协调器
负责协调整个股票分析流程，管理分析师团队和资源配置
"""

from typing import Dict, List, Any, Optional, Callable
import uuid
import logging
from datetime import datetime
from dataclasses import dataclass, field

from tradingagents.exceptions import (
    AnalysisError, ConfigurationError, handle_exceptions
)
from tradingagents.utils.logging_init import get_logger
from .analysis_config import AnalysisConfig, AnalystConfig
from .progress_tracker import AnalysisProgressTracker

logger = get_logger(__name__)


@dataclass
class AnalysisRequest:
    """分析请求"""
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    stock_symbol: str = ""
    analysis_date: str = ""
    analysts: List[str] = field(default_factory=list)
    research_depth: int = 3
    market_type: str = "美股"
    config: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    user_id: Optional[str] = None


@dataclass
class AnalysisContext:
    """分析上下文"""
    request: AnalysisRequest
    state: Dict[str, Any] = field(default_factory=dict)
    results: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    progress_tracker: Optional[AnalysisProgressTracker] = None


class AnalysisCoordinator:
    """分析协调器"""

    def __init__(self, analysis_config: AnalysisConfig):
        """
        初始化分析协调器

        Args:
            analysis_config: 分析配置
        """
        self.config = analysis_config
        self.active_analysis = {}  # request_id -> AnalysisContext
        self.analysis_history = {}  # request_id -> AnalysisContext

        logger.info("🎯 分析协调器初始化完成")

    @handle_exceptions({
            ConfigurationError: AnalysisError,
            Exception: AnalysisError
        })
    def start_analysis(self, request: AnalysisRequest,
                       progress_callback: Optional[Callable] = None) -> str:
        """
        启动分析

        Args:
            request: 分析请求
            progress_callback: 进度回调函数

        Returns:
            str: 分析请求ID

        Raises:
            AnalysisError: 分析启动失败
        """
        try:
            logger.info(f"🚀 启动分析: {request.stock_symbol}")

            # 1. 验证分析请求
            self._validate_analysis_request(request)

            # 2. 创建分析上下文
            context = self._create_analysis_context(request, progress_callback)

            # 3. 初始化分析状态
            self._initialize_analysis_state(context)

            # 4. 注册活跃分析
            self.active_analysis[request.request_id] = context

            # 5. 开始分析流程
            self._execute_analysis_workflow(context)

            logger.info(f"✅ 分析启动成功: {request.request_id}")
            return request.request_id

        except Exception as e:
            logger.error(f"❌ 分析启动失败: {e}")
            raise AnalysisError(f"分析启动失败: {e}", 'ANALYSIS_START_FAILED')

    def get_analysis_status(self, request_id: str) -> Optional[Dict[str, Any]]:
        """
        获取分析状态

        Args:
            request_id: 分析请求ID

        Returns:
            Optional[Dict[str, Any]]: 分析状态信息
        """
        try:
            # 检查活跃分析
            if request_id in self.active_analysis:
                context = self.active_analysis[request_id]
                return self._build_status_response(context, 'running')

            # 检查历史分析
            elif request_id in self.analysis_history:
                context = self.analysis_history[request_id]
                return self._build_status_response(context, 'completed')

            else:
                return None

        except Exception as e:
            logger.error(f"获取分析状态失败: {e}")
            return None

    def cancel_analysis(self, request_id: str) -> bool:
        """
        取消分析

        Args:
            request_id: 分析请求ID

        Returns:
            bool: 是否成功取消
        """
        try:
            if request_id in self.active_analysis:
                context = self.active_analysis[request_id]

                # 标记为取消
                context.state['cancelled'] = True

                # 清理资源
                if context.progress_tracker:
                    context.progress_tracker.cancel()

                # 移动到历史记录
                self.analysis_history[request_id] = context
                del self.active_analysis[request_id]

                logger.info(f"✅ 分析已取消: {request_id}")
                return True

            return False

        except Exception as e:
            logger.error(f"取消分析失败: {e}")
            return False

    def get_analysis_result(self, request_id: str) -> Optional[Dict[str, Any]]:
        """
        获取分析结果

        Args:
            request_id: 分析请求ID

        Returns:
            Optional[Dict[str, Any]]: 分析结果
        """
        try:
            if request_id in self.analysis_history:
                context = self.analysis_history[request_id]
                return context.results

            return None

        except Exception as e:
            logger.error(f"获取分析结果失败: {e}")
            return None

    def cleanup_old_analysis(self, max_age_hours: int = 24):
        """
        清理旧的分析记录

        Args:
            max_age_hours: 最大保留时间（小时）
        """
        try:
            current_time = datetime.now()
            to_remove = []

            for request_id, context in self.analysis_history.items():
                age_hours = (current_time - context.request.created_at).total_seconds() / 3600
                if age_hours > max_age_hours:
                    to_remove.append(request_id)

            for request_id in to_remove:
                del self.analysis_history[request_id]

            logger.info(f"🧹 清理了 {len(to_remove)} 个旧分析记录")

        except Exception as e:
            logger.error(f"清理旧分析记录失败: {e}")

    def _validate_analysis_request(self, request: AnalysisRequest):
        """验证分析请求"""
        if not request.stock_symbol:
            raise ConfigurationError('stock_symbol', request.stock_symbol, '股票代码不能为空')

        if not request.analysis_date:
            raise ConfigurationError('analysis_date', request.analysis_date, '分析日期不能为空')

        if not request.analysts:
            request.analysts = self.config.default_analysts

        if request.research_depth < 1 or request.research_depth > 5:
            raise ConfigurationError('research_depth', request.research_depth, '研究深度必须在1-5之间')

        logger.debug(f"✅ 分析请求验证通过: {request.stock_symbol}")

    def _create_analysis_context(self, request: AnalysisRequest,
                               progress_callback: Optional[Callable]) -> AnalysisContext:
        """创建分析上下文"""
        # 创建进度跟踪器
        progress_tracker = AnalysisProgressTracker(
            request_id=request.request_id,
            total_steps=self._calculate_total_steps(request),
            progress_callback=progress_callback
        )

        # 初始化状态
        state = {
            'stock_symbol': request.stock_symbol,
            'analysis_date': request.analysis_date,
            'analysts': request.analysts,
            'research_depth': request.research_depth,
            'market_type': request.market_type,
            'config': request.config,
            'cancelled': False,
            'current_step': 0,
            'total_steps': progress_tracker.total_steps
        }

        return AnalysisContext(
            request=request,
            state=state,
            progress_tracker=progress_tracker
        )

    def _initialize_analysis_state(self, context: AnalysisContext):
        """初始化分析状态"""
        try:
            # 获取股票市场信息
            from tradingagents.utils.stock_utils import StockUtils
            stock_utils = StockUtils()

            market_info = stock_utils.get_market_info(context.request.stock_symbol)
            context.state['market_info'] = market_info

            # 初始化消息历史
            context.state['messages'] = []

            # 初始化分析师结果
            context.state['analyst_results'] = {}

            # 初始化市场分析师结果
            context.state['market_analysis'] = None

            logger.debug(f"✅ 分析状态初始化完成: {context.request.stock_symbol}")

        except Exception as e:
            logger.error(f"初始化分析状态失败: {e}")
            raise AnalysisError(f"分析状态初始化失败: {e}", 'STATE_INITIALIZATION_FAILED')

    def _execute_analysis_workflow(self, context: AnalysisContext):
        """执行分析工作流"""
        try:
            # 启动异步分析
            import threading
            analysis_thread = threading.Thread(
                target=self._run_analysis_workflow,
                args=(context,),
                daemon=True
            )
            analysis_thread.start()

        except Exception as e:
            logger.error(f"启动分析工作流失败: {e}")
            raise AnalysisError(f"分析工作流启动失败: {e}", 'WORKFLOW_START_FAILED')

    def _run_analysis_workflow(self, context: AnalysisContext):
        """运行分析工作流（在线程中执行）"""
        try:
            logger.info(f"🔄 开始分析工作流: {context.request.stock_symbol}")

            # 1. 市场分析师分析
            if not context.state.get('cancelled'):
                self._execute_market_analyst(context)

            # 2. 基本面分析师分析
            if not context.state.get('cancelled'):
                self._execute_fundamentals_analyst(context)

            # 3. 新闻分析师分析
            if not context.state.get('cancelled') and '新闻分析师' in context.request.analysts:
                self._execute_news_analyst(context)

            # 4. 社交媒体分析师分析
            if not context.state.get('cancelled') and '社交媒体分析师' in context.request.analysts:
                self._execute_social_media_analyst(context)

            # 5. 中国市场分析师分析
            if not context.state.get('cancelled') and '中国市场分析师' in context.request.analysts:
                self._execute_china_market_analyst(context)

            # 6. 研究主管协调
            if not context.state.get('cancelled'):
                self._execute_research_manager(context)

            # 7. 风险评估
            if not context.state.get('cancelled'):
                self._execute_risk_assessment(context)

            # 8. 交易决策
            if not context.state.get('cancelled'):
                self._execute_trader(context)

            # 9. 完成分析
            self._complete_analysis(context)

        except Exception as e:
            logger.error(f"分析工作流执行失败: {e}")
            context.errors.append(f"分析工作流执行失败: {str(e)}")
            self._fail_analysis(context, str(e))

    def _execute_market_analyst(self, context: AnalysisContext):
        """执行市场分析师"""
        try:
            self._update_progress(context, "市场技术分析", 10)

            # 这里应该调用实际的市场分析师
            # 模拟分析结果
            market_analysis = {
                'technical_indicators': {
                    'rsi': 65.5,
                    'macd': 0.12,
                    'bollinger_position': 'upper'
                },
                'price_action': {
                    'trend': 'uptrend',
                    'support': 145.50,
                    'resistance': 152.30
                },
                'recommendation': '买入'
            }

            context.state['market_analysis'] = market_analysis
            context.results['market_analysis'] = market_analysis

            logger.debug(f"✅ 市场分析师分析完成: {context.request.stock_symbol}")

        except Exception as e:
            logger.error(f"市场分析师分析失败: {e}")
            context.errors.append(f"市场分析师分析失败: {str(e)}")

    def _execute_fundamentals_analyst(self, context: AnalysisContext):
        """执行基本面分析师"""
        try:
            self._update_progress(context, "基本面分析", 25)

            # 这里应该调用实际的基本面分析师
            # 模拟分析结果
            fundamentals_analysis = {
                'financial_ratios': {
                    'roe': 18.5,
                    'pe_ratio': 22.3,
                    'debt_to_equity': 0.45
                },
                'financial_health': '良好',
                'recommendation': '买入'
            }

            context.state['fundamentals_analysis'] = fundamentals_analysis
            context.results['fundamentals_analysis'] = fundamentals_analysis

            logger.debug(f"✅ 基本面分析师分析完成: {context.request.stock_symbol}")

        except Exception as e:
            logger.error(f"基本面分析师分析失败: {e}")
            context.errors.append(f"基本面分析师分析失败: {str(e)}")

    def _execute_news_analyst(self, context: AnalysisContext):
        """执行新闻分析师"""
        try:
            self._update_progress(context, "新闻分析", 40)

            # 模拟新闻分析结果
            news_analysis = {
                'sentiment': 'positive',
                'key_news': [
                    '公司发布超预期财报',
                    '获得重要合同'
                ],
                'impact_assessment': '利好',
                'recommendation': '买入'
            }

            context.state['news_analysis'] = news_analysis
            context.results['news_analysis'] = news_analysis

            logger.debug(f"✅ 新闻分析师分析完成: {context.request.stock_symbol}")

        except Exception as e:
            logger.error(f"新闻分析师分析失败: {e}")
            context.errors.append(f"新闻分析师分析失败: {str(e)}")

    def _execute_social_media_analyst(self, context: AnalysisContext):
        """执行社交媒体分析师"""
        try:
            self._update_progress(context, "社交媒体分析", 55)

            # 模拟社交媒体分析结果
            social_analysis = {
                'sentiment_score': 7.2,
                'discussion_volume': 'high',
                'key_topics': [
                    '财报超预期',
                    '新产品发布'
                ],
                'recommendation': '买入'
            }

            context.state['social_analysis'] = social_analysis
            context.results['social_analysis'] = social_analysis

            logger.debug(f"✅ 社交媒体分析师分析完成: {context.request.stock_symbol}")

        except Exception as e:
            logger.error(f"社交媒体分析师分析失败: {e}")
            context.errors.append(f"社交媒体分析师分析失败: {str(e)}")

    def _execute_china_market_analyst(self, context: AnalysisContext):
        """执行中国市场分析师"""
        try:
            self._update_progress(context, "中国市场分析", 70)

            # 模拟中国市场分析结果
            china_analysis = {
                'policy_impact': 'positive',
                'market_sentiment': 'bullish',
                'sector_outlook': 'favorable',
                'recommendation': '买入'
            }

            context.state['china_analysis'] = china_analysis
            context.results['china_analysis'] = china_analysis

            logger.debug(f"✅ 中国市场分析师分析完成: {context.request.stock_symbol}")

        except Exception as e:
            logger.error(f"中国市场分析师分析失败: {e}")
            context.errors.append(f"中国市场分析师分析失败: {str(e)}")

    def _execute_research_manager(self, context: AnalysisContext):
        """执行研究主管"""
        try:
            self._update_progress(context, "研究主管协调", 80)

            # 综合各分析师意见
            research_summary = {
                'bull_case': self._generate_bull_case(context),
                'bear_case': self._generate_bear_case(context),
                'consensus': 'bullish',
                'confidence': 75
            }

            context.state['research_summary'] = research_summary
            context.results['research_summary'] = research_summary

            logger.debug(f"✅ 研究主管协调完成: {context.request.stock_symbol}")

        except Exception as e:
            logger.error(f"研究主管协调失败: {e}")
            context.errors.append(f"研究主管协调失败: {str(e)}")

    def _execute_risk_assessment(self, context: AnalysisContext):
        """执行风险评估"""
        try:
            self._update_progress(context, "风险评估", 90)

            # 模拟风险评估结果
            risk_assessment = {
                'risk_level': 'medium',
                'key_risks': [
                    '市场波动风险',
                    '估值回调风险'
                ],
                'risk_score': 6.5,
                'recommendation': '适度配置'
            }

            context.state['risk_assessment'] = risk_assessment
            context.results['risk_assessment'] = risk_assessment

            logger.debug(f"✅ 风险评估完成: {context.request.stock_symbol}")

        except Exception as e:
            logger.error(f"风险评估失败: {e}")
            context.errors.append(f"风险评估失败: {str(e)}")

    def _execute_trader(self, context: AnalysisContext):
        """执行交易决策"""
        try:
            self._update_progress(context, "交易决策", 95)

            # 基于所有分析结果做出交易决策
            trading_decision = {
                'action': '买入',
                'confidence': 78,
                'position_size': 'medium',
                'target_price': 165.50,
                'stop_loss': 148.20,
                'holding_period': '6-12个月'
            }

            context.state['trading_decision'] = trading_decision
            context.results['trading_decision'] = trading_decision

            logger.debug(f"✅ 交易决策完成: {context.request.stock_symbol}")

        except Exception as e:
            logger.error(f"交易决策失败: {e}")
            context.errors.append(f"交易决策失败: {str(e)}")

    def _complete_analysis(self, context: AnalysisContext):
        """完成分析"""
        try:
            self._update_progress(context, "分析完成", 100)

            # 生成最终报告
            final_report = self._generate_final_report(context)
            context.results['final_report'] = final_report

            # 移动到历史记录
            request_id = context.request.request_id
            self.analysis_history[request_id] = context

            if request_id in self.active_analysis:
                del self.active_analysis[request_id]

            logger.info(f"✅ 分析完成: {context.request.stock_symbol}")

        except Exception as e:
            logger.error(f"完成分析失败: {e}")
            context.errors.append(f"完成分析失败: {str(e)}")

    def _fail_analysis(self, context: AnalysisContext, error_message: str):
        """分析失败"""
        try:
            context.state['failed'] = True
            context.state['error_message'] = error_message

            # 移动到历史记录
            request_id = context.request.request_id
            self.analysis_history[request_id] = context

            if request_id in self.active_analysis:
                del self.active_analysis[request_id]

            logger.error(f"❌ 分析失败: {context.request.stock_symbol} - {error_message}")

        except Exception as e:
            logger.error(f"处理分析失败时出错: {e}")

    def _update_progress(self, context: AnalysisContext, step_name: str, progress: int):
        """更新进度"""
        if context.progress_tracker:
            context.progress_tracker.update_progress(step_name, progress)

        context.state['current_step'] = progress

    def _calculate_total_steps(self, request: AnalysisRequest) -> int:
        """计算总步骤数"""
        base_steps = 9  # 基础分析步骤
        additional_steps = 0

        # 根据分析师数量调整
        if '新闻分析师' in request.analysts:
            additional_steps += 1
        if '社交媒体分析师' in request.analysts:
            additional_steps += 1
        if '中国市场分析师' in request.analysts:
            additional_steps += 1

        return base_steps + additional_steps

    def _build_status_response(self, context: AnalysisContext, status: str) -> Dict[str, Any]:
        """构建状态响应"""
        return {
            'request_id': context.request.request_id,
            'stock_symbol': context.request.stock_symbol,
            'status': status,
            'progress': context.state.get('current_step', 0),
            'total_steps': context.state.get('total_steps', 0),
            'current_step': context.progress_tracker.current_step if context.progress_tracker else '',
            'errors': context.errors,
            'warnings': context.warnings,
            'created_at': context.request.created_at.isoformat(),
            'updated_at': datetime.now().isoformat()
        }

    def _generate_bull_case(self, context: AnalysisContext) -> str:
        """生成看涨理由"""
        reasons = []

        if context.results.get('market_analysis', {}).get('recommendation') == '买入':
            reasons.append("技术指标显示上涨趋势")

        if context.results.get('fundamentals_analysis', {}).get('recommendation') == '买入':
            reasons.append("基本面强劲，财务状况良好")

        if context.results.get('news_analysis', {}).get('sentiment') == 'positive':
            reasons.append("新闻情绪积极")

        if context.results.get('social_analysis', {}).get('sentiment_score', 0) > 6:
            reasons.append("社交媒体讨论热度高")

        return "; ".join(reasons) if reasons else "综合分析显示积极因素"

    def _generate_bear_case(self, context: AnalysisContext) -> str:
        """生成看跌理由"""
        reasons = []

        if context.results.get('risk_assessment', {}).get('risk_level') in ['high', 'medium']:
            reasons.append("存在一定市场风险")

        if context.results.get('market_analysis', {}).get('recommendation') == '卖出':
            reasons.append("技术指标显示下跌趋势")

        return "; ".join(reasons) if reasons else "需要关注潜在风险因素"

    def _generate_final_report(self, context: AnalysisContext) -> Dict[str, Any]:
        """生成最终报告"""
        return {
            'summary': {
                'action': context.results.get('trading_decision', {}).get('action', '持有'),
                'confidence': context.results.get('trading_decision', {}).get('confidence', 0),
                'target_price': context.results.get('trading_decision', {}).get('target_price', 0),
                'risk_level': context.results.get('risk_assessment', {}).get('risk_level', '未知')
            },
            'detailed_analysis': {
                'market': context.results.get('market_analysis', {}),
                'fundamentals': context.results.get('fundamentals_analysis', {}),
                'news': context.results.get('news_analysis', {}),
                'social': context.results.get('social_analysis', {}),
                'research': context.results.get('research_summary', {}),
                'risk': context.results.get('risk_assessment', {})
            },
            'recommendations': context.results.get('trading_decision', {}),
            'metadata': {
                'request_id': context.request.request_id,
                'stock_symbol': context.request.stock_symbol,
                'analysis_date': context.request.analysis_date,
                'analysts': context.request.analysts,
                'research_depth': context.request.research_depth,
                'completed_at': datetime.now().isoformat(),
                'errors': context.errors,
                'warnings': context.warnings
            }
        }