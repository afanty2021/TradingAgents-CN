"""
TradingAgents-CN 统一异常处理系统
提供清晰的异常层次结构和错误处理机制
"""

from typing import Optional, Any, Dict
import logging

logger = logging.getLogger(__name__)


class TradingAgentsError(Exception):
    """TradingAgents 基础异常类"""

    def __init__(self, message: str, error_code: Optional[str] = None,
                 context: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.context = context or {}

        # 记录异常
        logger.error(f"{self.error_code}: {self.message}", extra=self.context)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'error_type': self.__class__.__name__,
            'error_code': self.error_code,
            'message': self.message,
            'context': self.context
        }


class DataFetchError(TradingAgentsError):
    """数据获取相关异常"""
    pass


class APIConnectionError(DataFetchError):
    """API连接异常"""

    def __init__(self, provider: str, endpoint: str, original_error: Exception):
        message = f"无法连接到 {provider} API: {endpoint}"
        context = {
            'provider': provider,
            'endpoint': endpoint,
            'original_error': str(original_error)
        }
        super().__init__(message, 'API_CONNECTION_ERROR', context)


class DataValidationError(DataFetchError):
    """数据验证异常"""

    def __init__(self, field_name: str, value: Any, validation_rule: str):
        message = f"数据验证失败 - {field_name}: {value} (规则: {validation_rule})"
        context = {
            'field_name': field_name,
            'value': str(value),
            'validation_rule': validation_rule
        }
        super().__init__(message, 'DATA_VALIDATION_ERROR', context)


class AnalysisError(TradingAgentsError):
    """分析过程异常"""
    pass


class ModelInferenceError(AnalysisError):
    """模型推理异常"""

    def __init__(self, model_name: str, provider: str, original_error: Exception):
        message = f"模型推理失败 - {provider}/{model_name}: {original_error}"
        context = {
            'model_name': model_name,
            'provider': provider,
            'original_error': str(original_error)
        }
        super().__init__(message, 'MODEL_INFERENCE_ERROR', context)


class InsufficientDataError(AnalysisError):
    """数据不足异常"""

    def __init__(self, data_type: str, required: int, available: int):
        message = f"{data_type}数据不足 - 需要: {required}, 可用: {available}"
        context = {
            'data_type': data_type,
            'required': required,
            'available': available
        }
        super().__init__(message, 'INSUFFICIENT_DATA_ERROR', context)


class ConfigurationError(TradingAgentsError):
    """配置相关异常"""
    pass


class MissingConfigurationError(ConfigurationError):
    """缺失配置异常"""

    def __init__(self, config_key: str, config_file: Optional[str] = None):
        message = f"缺失必需配置: {config_key}"
        context = {'config_key': config_key}
        if config_file:
            message += f" (文件: {config_file})"
            context['config_file'] = config_file
        super().__init__(message, 'MISSING_CONFIGURATION_ERROR', context)


class InvalidConfigurationError(ConfigurationError):
    """无效配置异常"""

    def __init__(self, config_key: str, value: Any, expected_type: str):
        message = f"无效配置值 - {config_key}: {value} (期望类型: {expected_type})"
        context = {
            'config_key': config_key,
            'value': str(value),
            'expected_type': expected_type
        }
        super().__init__(message, 'INVALID_CONFIGURATION_ERROR', context)


class SecurityError(TradingAgentsError):
    """安全相关异常"""
    pass


class AuthenticationError(SecurityError):
    """认证异常"""

    def __init__(self, provider: str, reason: str):
        message = f"{provider} 认证失败: {reason}"
        context = {'provider': provider, 'reason': reason}
        super().__init__(message, 'AUTHENTICATION_ERROR', context)


class PermissionError(SecurityError):
    """权限异常"""

    def __init__(self, resource: str, required_permission: str, user_role: str):
        message = f"权限不足 - 访问 {resource} 需要 {required_permission}, 当前角色: {user_role}"
        context = {
            'resource': resource,
            'required_permission': required_permission,
            'user_role': user_role
        }
        super().__init__(message, 'PERMISSION_ERROR', context)


class CacheError(TradingAgentsError):
    """缓存相关异常"""
    pass


class CacheConnectionError(CacheError):
    """缓存连接异常"""

    def __init__(self, cache_type: str, connection_string: str):
        message = f"无法连接到 {cache_type}: {connection_string}"
        context = {
            'cache_type': cache_type,
            'connection_string': connection_string
        }
        super().__init__(message, 'CACHE_CONNECTION_ERROR', context)


class ValidationError(TradingAgentsError):
    """输入验证异常"""

    def __init__(self, field: str, value: Any, constraint: str):
        message = f"输入验证失败 - {field}: {value} (约束: {constraint})"
        context = {
            'field': field,
            'value': str(value),
            'constraint': constraint
        }
        super().__init__(message, 'VALIDATION_ERROR', context)


# 异常处理装饰器
def handle_exceptions(exception_map: Optional[Dict[type, type]] = None):
    """
    异常处理装饰器

    Args:
        exception_map: 异常映射字典，将原始异常映射为自定义异常
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # 如果有异常映射，转换异常类型
                if exception_map and type(e) in exception_map:
                    custom_exception = exception_map[type(e)]
                    raise custom_exception(str(e))

                # 如果是自定义异常，直接抛出
                if isinstance(e, TradingAgentsError):
                    raise

                # 其他异常包装为通用异常
                raise TradingAgentsError(f"未预期的错误: {str(e)}",
                                      'UNEXPECTED_ERROR',
                                      {'original_type': type(e).__name__})
        return wrapper
    return decorator


# 重试机制
def retry_on_exception(max_retries: int = 3, delay: float = 1.0,
                      exceptions: tuple = (Exception,)):
    """
    异常重试装饰器

    Args:
        max_retries: 最大重试次数
        delay: 重试间隔(秒)
        exceptions: 需要重试的异常类型
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(f"第 {attempt + 1} 次尝试失败: {str(e)}, {delay}秒后重试...")
                        time.sleep(delay * (2 ** attempt))  # 指数退避
                    else:
                        logger.error(f"达到最大重试次数 {max_retries}, 放弃重试")

            raise last_exception
        return wrapper
    return decorator


# 导入time模块用于重试机制
import time