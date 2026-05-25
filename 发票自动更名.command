#!/bin/bash
# 发票自动更名程序 - 双击运行此文件即可自动重命名同目录下的 PDF 发票

cd "$(dirname "$0")"
python3 rename_invoices.py --execute
echo ""
echo "按任意键关闭窗口..."
read -n 1 -s
