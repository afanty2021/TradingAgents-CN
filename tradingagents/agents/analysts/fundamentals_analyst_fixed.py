"""
基本面分析师 - 修复命名版本
正确使用 analyst 而不是 analist
"""

from .fundamentals import create_fundamentals_analyst

# 重新导出正确的命名
__all__ = ['create_fundamentals_analyst']