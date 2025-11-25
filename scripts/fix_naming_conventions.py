#!/usr/bin/env python3
"""
修复命名规范脚本
统一修复项目中的命名不一致问题
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# 需要修复的命名映射
NAMING_FIXES = {
    # analyst -> analyst (拼写错误)
    r'\banalyst\b': 'analyst',
    r'\banalysts\b': 'analysts',
    r'\bAnalyst\b': 'Analyst',
    r'\bAnalysts\b': 'Analysts',

    # propagate -> propagate (拼写错误)
    r'\bpropagate\b': 'propagate',
    r'\bPropagate\b': 'Propagate',
    r'\bpropagation\b': 'propagation',
    r'\bPropagation\b': 'Propagation',

    # 其他常见命名问题
    r'\bsetup\b': 'setup',
    r'\bSetup\b': 'Setup',
    r'\bconfig\b': 'config',
    r'\bConfig\b': 'Config',
}

# 需要忽略的文件和目录
IGNORE_PATTERNS = [
    r'\.git',
    r'__pycache__',
    r'\.venv',
    r'node_modules',
    r'\.pytest_cache',
    r'\.coverage',
    r'build',
    r'dist',
    r'\.env',
    r'\.log',
    r'\.tmp'
]

# 文件扩展名白名单
ALLOWED_EXTENSIONS = {
    '.py',
    '.md',
    '.json',
    '.yaml',
    '.yml',
    '.toml',
    '.txt',
    '.sh',
    '.js',
    '.jsx',
    '.ts',
    '.tsx',
    '.html',
    '.css'
}


def should_ignore_file(file_path: Path) -> bool:
    """检查是否应该忽略文件"""
    path_str = str(file_path)

    for pattern in IGNORE_PATTERNS:
        if re.search(pattern, path_str):
            return True

    return False


def has_allowed_extension(file_path: Path) -> bool:
    """检查文件是否有允许的扩展名"""
    return file_path.suffix.lower() in ALLOWED_EXTENSIONS


def fix_file_content(content: str, file_path: Path) -> Tuple[str, Dict[str, int]]:
    """修复文件内容中的命名问题"""
    fixed_content = content
    changes = {}

    for pattern, replacement in NAMING_FIXES.items():
        matches = re.findall(pattern, content)
        if matches:
            count = len(matches)
            changes[pattern] = count
            fixed_content = re.sub(pattern, replacement, fixed_content)

    return fixed_content, changes


def fix_filename(file_path: Path) -> Path:
    """修复文件名中的命名问题"""
    new_name = file_path.name

    for pattern, replacement in NAMING_FIXES.items():
        if re.search(pattern, new_name):
            new_name = re.sub(pattern, replacement, new_name)

    if new_name != file_path.name:
        return file_path.parent / new_name

    return file_path


def process_file(file_path: Path, dry_run: bool = False) -> Dict[str, any]:
    """处理单个文件"""
    result = {
        'file_path': str(file_path),
        'content_changes': {},
        'filename_changed': False,
        'old_filename': '',
        'new_filename': ''
    }

    try:
        # 检查并修复文件名
        new_file_path = fix_filename(file_path)
        if new_file_path != file_path:
            result['filename_changed'] = True
            result['old_filename'] = file_path.name
            result['new_filename'] = new_file_path.name

            if not dry_run:
                # 重命名文件
                file_path.rename(new_file_path)
                file_path = new_file_path

        # 读取并修复文件内容
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        fixed_content, changes = fix_file_content(content, file_path)

        if changes:
            result['content_changes'] = changes

            if not dry_run:
                # 写回修复后的内容
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)

        return result

    except Exception as e:
        result['error'] = str(e)
        return result


def print_summary(results: List[Dict[str, any]], dry_run: bool = False):
    """打印修复摘要"""
    total_files = len(results)
    files_with_changes = sum(1 for r in results if (r['content_changes'] or r['filename_changed']))
    total_content_changes = sum(sum(r['content_changes'].values()) for r in results)
    filename_changes = sum(1 for r in results if r['filename_changed'])

    print(f"\n📊 命名规范修复摘要 ({'DRY RUN' if dry_run else 'EXECUTED'})")
    print("=" * 60)
    print(f"📁 处理文件总数: {total_files}")
    print(f"🔧 有变更的文件: {files_with_changes}")
    print(f"📝 内容修复总数: {total_content_changes}")
    print(f"📂 文件名修复数: {filename_changes}")

    if total_content_changes > 0:
        print(f"\n📋 详细修复内容:")
        pattern_descriptions = {
            r'\banalyst\b': 'analyst (拼写错误)',
            r'\banalysts\b': 'analysts (拼写错误)',
            r'\bAnalyst\b': 'Analyst (拼写错误)',
            r'\bAnalysts\b': 'Analysts (拼写错误)',
            r'\bpropagate\b': 'propagate (拼写错误)',
            r'\bPropagate\b': 'Propagate (拼写错误)',
            r'\bpropagation\b': 'propagation (拼写错误)',
            r'\bPropagation\b': 'Propagation (拼写错误)',
        }

        for pattern, description in pattern_descriptions.items():
            total_fixes = sum(r['content_changes'].get(pattern, 0) for r in results)
            if total_fixes > 0:
                print(f"  • {description}: {total_fixes} 处")

    if filename_changes > 0:
        print(f"\n📂 文件名修复:")
        for result in results:
            if result['filename_changed']:
                print(f"  • {result['old_filename']} -> {result['new_filename']}")

    if dry_run:
        print(f"\n💡 这是DRY RUN，没有实际修改文件。")
        print(f"   要执行修复，请运行: python {__file__} --execute")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='修复项目命名规范')
    parser.add_argument('--execute', action='store_true',
                       help='实际执行修复（默认为dry-run）')
    parser.add_argument('--path', type=str, default=str(PROJECT_ROOT),
                       help='要处理的项目路径')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='详细输出')

    args = parser.parse_args()

    dry_run = not args.execute
    project_path = Path(args.path)

    if not project_path.exists():
        print(f"❌ 路径不存在: {project_path}")
        sys.exit(1)

    print(f"🔍 扫描项目: {project_path}")
    print(f"🔧 修复模式: {'DRY RUN' if dry_run else 'EXECUTE'}")

    # 查找所有需要处理的文件
    files_to_process = []

    for file_path in project_path.rglob('*'):
        if (file_path.is_file() and
            has_allowed_extension(file_path) and
            not should_ignore_file(file_path)):
            files_to_process.append(file_path)

    print(f"📁 找到 {len(files_to_process)} 个文件需要检查")

    # 处理文件
    results = []

    for i, file_path in enumerate(files_to_process, 1):
        if args.verbose:
            print(f"🔧 处理 ({i}/{len(files_to_process)}): {file_path}")

        result = process_file(file_path, dry_run)
        results.append(result)

    # 打印摘要
    print_summary(results, dry_run)


if __name__ == '__main__':
    main()