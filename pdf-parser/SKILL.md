---
name: ai-content-automation-pdf-parser
description: PDF和MD文档解析模块。提取文本内容、生成结构化大纲、提取知识点和重点。
---

# PDF解析模块

## 功能

- 解析 PDF 文件，提取文本、表格、图片
- 解析 MD 文件，保持结构
- 生成结构化大纲（JSON格式）
- 提取关键知识点

## 使用方式

```bash
# 解析PDF
python -m pdf_parser --input document.pdf --output outline.json

# 解析MD
python -m pdf_parser --input README.md --output outline.json

# 仅提取文本
python -m pdf_parser --input document.pdf --mode text --output content.txt
```

## 输出格式

```json
{
  "title": "文档标题",
  "sections": [
    {
      "level": 1,
      "title": "第一章",
      "content": "章节内容摘要",
      "key_points": ["要点1", "要点2"]
    }
  ],
  "metadata": {
    "pages": 50,
    "author": "作者名",
    "date": "2024-01-01"
  }
}
```

## 依赖

- pdfplumber
- pymupdf
- markdown
