#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代码质量检查脚本
检查项目中的代码质量问题并提供改进建议
"""

import os
import ast
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import json
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class CodeQualityChecker:
    """代码质量检查器"""

    def __init__(self):
        self.project_root = project_root
        self.issues = []
        self.stats = {
            'files_checked': 0,
            'functions_with_types': 0,
            'functions_without_types': 0,
            'classes_with_docs': 0,
            'functions_with_docs': 0,
            'imports_star': 0,
            'complex_functions': 0,
            'lines_of_code': 0
        }

    def check_directory(self, directory: str) -> Dict[str, Any]:
        """检查目录中的Python文件"""
        directory_path = self.project_root / directory
        if not directory_path.exists():
            return {'error': f'Directory {directory} not found'}

        for py_file in directory_path.rglob('*.py'):
            if '__pycache__' in str(py_file):
                continue
            self.check_file(py_file)

        return self.generate_report()

    def check_file(self, file_path: Path) -> None:
        """检查单个Python文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 解析AST
            try:
                tree = ast.parse(content)
            except SyntaxError as e:
                self.issues.append({
                    'type': 'syntax_error',
                    'file': str(file_path),
                    'line': e.lineno,
                    'message': f'语法错误: {e.msg}'
                })
                return

            self.stats['files_checked'] += 1
            self.stats['lines_of_code'] += len(content.splitlines())

            # 检查各种质量问题
            self.check_type_annotations(tree, file_path)
            self.check_docstrings(tree, file_path)
            self.check_imports(tree, file_path)
            self.check_complexity(tree, file_path, content)

        except Exception as e:
            self.issues.append({
                'type': 'file_error',
                'file': str(file_path),
                'message': f'文件检查错误: {str(e)}'
            })

    def check_type_annotations(self, tree: ast.AST, file_path: Path) -> None:
        """检查类型注解"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                has_return_type = node.returns is not None
                has_param_types = all(
                    arg.annotation is not None
                    for arg in node.args.args
                )

                if has_return_type and has_param_types:
                    self.stats['functions_with_types'] += 1
                else:
                    self.stats['functions_without_types'] += 1
                    if not node.name.startswith('_'):  # 忽略私有函数
                        self.issues.append({
                            'type': 'missing_type_annotation',
                            'file': str(file_path),
                            'line': node.lineno,
                            'function': node.name,
                            'message': f'函数 {node.name} 缺少完整的类型注解'
                        })

    def check_docstrings(self, tree: ast.AST, file_path: Path) -> None:
        """检查文档字符串"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if (ast.get_docstring(node) is not None and
                    len(ast.get_docstring(node).strip()) > 10):
                    self.stats['classes_with_docs'] += 1
                else:
                    self.issues.append({
                        'type': 'missing_class_docstring',
                        'file': str(file_path),
                        'line': node.lineno,
                        'class': node.name,
                        'message': f'类 {node.name} 缺少文档字符串'
                    })

            elif isinstance(node, ast.FunctionDef):
                if (ast.get_docstring(node) is not None and
                    len(ast.get_docstring(node).strip()) > 10):
                    self.stats['functions_with_docs'] += 1
                elif not node.name.startswith('_'):  # 忽略私有函数
                    self.issues.append({
                        'type': 'missing_function_docstring',
                        'file': str(file_path),
                        'line': node.lineno,
                        'function': node.name,
                        'message': f'函数 {node.name} 缺少文档字符串'
                    })

    def check_imports(self, tree: ast.AST, file_path: Path) -> None:
        """检查导入语句"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.names[0].name == '*':
                    self.stats['imports_star'] += 1
                    self.issues.append({
                        'type': 'star_import',
                        'file': str(file_path),
                        'line': node.lineno,
                        'module': node.module or '',
                        'message': f'使用 import * 违反代码规范'
                    })

    def check_complexity(self, tree: ast.AST, file_path: Path, content: str) -> None:
        """检查函数复杂度"""
        lines = content.splitlines()

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # 计算函数行数
                func_lines = node.end_lineno - node.lineno + 1 if hasattr(node, 'end_lineno') else 0

                # 简单的复杂度检查：行数超过50行
                if func_lines > 50:
                    self.stats['complex_functions'] += 1
                    self.issues.append({
                        'type': 'high_complexity',
                        'file': str(file_path),
                        'line': node.lineno,
                        'function': node.name,
                        'lines': func_lines,
                        'message': f'函数 {node.name} 过于复杂 ({func_lines} 行)'
                    })

    def generate_report(self) -> Dict[str, Any]:
        """生成质量报告"""
        total_functions = self.stats['functions_with_types'] + self.stats['functions_without_types']
        type_coverage = (
            self.stats['functions_with_types'] / total_functions * 100
            if total_functions > 0 else 0
        )

        return {
            'timestamp': datetime.now().isoformat(),
            'statistics': self.stats,
            'quality_metrics': {
                'type_annotation_coverage': f'{type_coverage:.1f}%',
                'docstring_coverage': f'{self.stats["functions_with_docs"] / max(total_functions, 1) * 100:.1f}%',
                'star_imports': self.stats['imports_star'],
                'complex_functions': self.stats['complex_functions'],
                'avg_lines_per_file': self.stats['lines_of_code'] / max(self.stats['files_checked'], 1)
            },
            'issues': self.issues,
            'summary': {
                'total_issues': len(self.issues),
                'critical_issues': len([i for i in self.issues if i['type'] in ['syntax_error', 'file_error']]),
                'style_issues': len([i for i in self.issues if i['type'] in ['star_import', 'missing_type_annotation']]),
                'documentation_issues': len([i for i in self.issues if 'docstring' in i['type']]),
                'complexity_issues': len([i for i in self.issues if i['type'] == 'high_complexity'])
            }
        }

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='代码质量检查工具')
    parser.add_argument('--directory', '-d', default='tradingagents',
                       help='要检查的目录 (默认: tradingagents)')
    parser.add_argument('--output', '-o', help='输出报告文件路径')
    parser.add_argument('--json', action='store_true', help='输出JSON格式')

    args = parser.parse_args()

    checker = CodeQualityChecker()
    report = checker.check_directory(args.directory)

    if args.json:
        output = json.dumps(report, ensure_ascii=False, indent=2)
    else:
        output = format_human_readable_report(report)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"✅ 质量报告已保存到: {args.output}")
    else:
        print(output)

def format_human_readable_report(report: Dict[str, Any]) -> str:
    """格式化人类可读的报告"""
    output = []
    output.append("📊 代码质量检查报告")
    output.append("=" * 50)
    output.append(f"检查时间: {report['timestamp']}")
    output.append("")

    # 统计信息
    stats = report['statistics']
    output.append("📈 统计信息:")
    output.append(f"  • 检查文件数: {stats['files_checked']}")
    output.append(f"  • 总代码行数: {stats['lines_of_code']}")
    output.append(f"  • 有类型注解的函数: {stats['functions_with_types']}")
    output.append(f"  • 无类型注解的函数: {stats['functions_without_types']}")
    output.append(f"  • 有文档字符串的函数: {stats['functions_with_docs']}")
    output.append(f"  • 有文档字符串的类: {stats['classes_with_docs']}")
    output.append("")

    # 质量指标
    metrics = report['quality_metrics']
    output.append("🎯 质量指标:")
    output.append(f"  • 类型注解覆盖率: {metrics['type_annotation_coverage']}")
    output.append(f"  • 文档字符串覆盖率: {metrics['docstring_coverage']}")
    output.append(f"  • 星号导入数量: {metrics['star_imports']}")
    output.append(f"  • 复杂函数数量: {metrics['complex_functions']}")
    output.append(f"  • 平均每文件行数: {metrics['avg_lines_per_file']:.1f}")
    output.append("")

    # 问题摘要
    summary = report['summary']
    output.append("⚠️ 问题摘要:")
    output.append(f"  • 总问题数: {summary['total_issues']}")
    output.append(f"  • 严重问题: {summary['critical_issues']}")
    output.append(f"  • 代码风格问题: {summary['style_issues']}")
    output.append(f"  • 文档问题: {summary['documentation_issues']}")
    output.append(f"  • 复杂度问题: {summary['complexity_issues']}")
    output.append("")

    # 详细问题列表（只显示前20个）
    issues = report['issues'][:20]
    if issues:
        output.append("🔍 详细问题 (前20个):")
        for issue in issues:
            file_path = Path(issue['file']).relative_to(project_root)
            output.append(f"  • {file_path}:{issue.get('line', '?')} - {issue['message']}")

    return "\n".join(output)

if __name__ == '__main__':
    main()