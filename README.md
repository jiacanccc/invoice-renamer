# 发票自动更名程序

一个用于 macOS 的 PDF 发票自动更名工具，自动识别文件夹内 PDF 发票中的发票号码，并将文件重命名为对应的发票号码。

## 适用场景

- 报销时需要按发票号码整理文件
- 财务归档需要统一命名
- 批量处理大量发票 PDF

## 使用方法

### 双击运行（推荐）

直接双击 `发票自动更名.command` 文件，程序会自动处理同目录下所有 PDF 发票文件。

### 命令行运行

```bash
# 预览模式（默认）- 查看将要进行的重命名操作
python3 rename_invoices.py --dir /path/to/folder

# 执行模式 - 实际执行重命名
python3 rename_invoices.py --dir /path/to/folder --execute
```

## 支持的发票类型

- 电子发票（普通发票）
- 电子发票（增值税专用发票）
- 电子发票（铁路电子客票）
- 其他符合 `发票号码` 格式的 PDF 发票

## 依赖

- Python 3
- pdftotext（Poppler）

安装 pdftotext：

```bash
# macOS
brew install poppler

# Ubuntu/Debian
sudo apt install poppler-utils
```

## 工作原理

1. 扫描指定目录下的所有 PDF 文件
2. 使用 pdftotext 提取 PDF 文本内容
3. 通过正则表达式匹配 `发票号码：XXXXXXXXXXXXXXXXXXXX` 格式
4. 支持全角和半角数字自动转换
5. 将文件重命名为对应的发票号码

## 注意事项

- 程序默认使用预览模式，确认无误后再使用 `--execute` 执行
- 如遇重名文件，会自动添加后缀 `_2`、`_3` 等
- 建议提前备份重要文件
