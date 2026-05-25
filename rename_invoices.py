#!/usr/bin/env python3
"""发票自动更名程序 - 从 PDF 中提取发票号码并重命名文件。"""

import argparse
import glob
import os
import re
import subprocess
import sys

# 全角数字转半角
FW_TO_HW = str.maketrans('０１２３４５６７８９', '0123456789')
INVOICE_PATTERN = re.compile(r'发票号码[：:]\s*([0-9０-９]{20})')


def check_pdftotext():
    """检查 pdftotext 是否已安装。"""
    try:
        subprocess.run(['pdftotext', '-v'], capture_output=True)
        return True
    except FileNotFoundError:
        return False


def extract_invoice_number(pdf_path):
    """从 PDF 文件中提取发票号码。"""
    try:
        result = subprocess.run(
            ['pdftotext', '-l', '1', pdf_path, '-'],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            return None
        match = INVOICE_PATTERN.search(result.stdout)
        if match:
            return match.group(1).translate(FW_TO_HW)
    except Exception:
        pass
    return None


def plan_renames(pdf_dir):
    """生成重命名计划。"""
    plan = []
    used_names = set()

    pdfs = sorted(glob.glob(os.path.join(pdf_dir, '*.pdf')) +
                  glob.glob(os.path.join(pdf_dir, '*.PDF')) +
                  glob.glob(os.path.join(pdf_dir, '*.Pdf')))
    # 去重（大小写不敏感）
    seen = set()
    unique_pdfs = []
    for p in pdfs:
        key = p.lower()
        if key not in seen:
            seen.add(key)
            unique_pdfs.append(p)

    for pdf_path in unique_pdfs:
        old_name = os.path.basename(pdf_path)
        invoice_num = extract_invoice_number(pdf_path)

        if not invoice_num:
            plan.append((pdf_path, None, 'SKIP'))
            continue

        new_name = f'{invoice_num}.pdf'

        # 目标名称与当前名称相同（忽略大小写）
        if old_name.lower() == new_name.lower():
            plan.append((pdf_path, pdf_path, 'SAME'))
            continue

        # 处理重名冲突
        target = os.path.join(pdf_dir, new_name)
        if target.lower() in used_names:
            counter = 2
            while True:
                candidate = os.path.join(pdf_dir, f'{invoice_num}_{counter}.pdf')
                if candidate.lower() not in used_names:
                    target = candidate
                    break
                counter += 1

        used_names.add(target.lower())
        plan.append((pdf_path, target, 'OK'))

    return plan


def execute_renames(plan, dry_run=True):
    """执行或预览重命名。"""
    success = skipped = collision = 0

    for old_path, new_path, status in plan:
        old_name = os.path.basename(old_path)

        if status == 'SKIP':
            print(f'  {old_name:<35} [跳过: 无法提取发票号码]')
            skipped += 1
        elif status == 'SAME':
            print(f'  {old_name:<35} [已是正确名称]')
            success += 1
        elif status == 'OK':
            new_name = os.path.basename(new_path)
            print(f'  {old_name:<35} -> {new_name}')
            if not dry_run:
                try:
                    os.rename(old_path, new_path)
                except OSError as e:
                    print(f'    错误: {e}')
                    skipped += 1
                    continue
            success += 1

    print()
    print(f'结果: {success} 成功, {skipped} 跳过')
    if dry_run:
        print('(预览模式 -- 文件未被重命名。使用 --execute 执行)')


def main():
    parser = argparse.ArgumentParser(description='发票自动更名程序')
    parser.add_argument('--dir', default=None,
                        help='PDF 文件目录（默认为脚本所在目录）')
    parser.add_argument('--execute', action='store_true',
                        help='执行重命名（默认为预览模式）')
    args = parser.parse_args()

    if not check_pdftotext():
        print('错误: 未找到 pdftotext，请先安装:')
        print('  macOS:   brew install poppler')
        print('  Ubuntu:  sudo apt install poppler-utils')
        sys.exit(1)

    pdf_dir = args.dir or os.path.dirname(os.path.abspath(__file__))
    if not os.path.isdir(pdf_dir):
        print(f'错误: 目录不存在: {pdf_dir}')
        sys.exit(2)

    print(f'扫描目录: {pdf_dir}')
    print()

    plan = plan_renames(pdf_dir)
    if not plan:
        print('未找到 PDF 文件。')
        sys.exit(2)

    execute_renames(plan, dry_run=not args.execute)


if __name__ == '__main__':
    main()
