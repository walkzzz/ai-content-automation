"""
PDF/MD文档解析模块
"""

import os
import json
import re


def parse_document(input_file, output_file):
    """解析PDF或MD文件，生成结构化大纲"""

    ext = os.path.splitext(input_file)[1].lower()

    if ext == ".pdf":
        content = parse_pdf(input_file)
    elif ext == ".md":
        content = parse_md(input_file)
    else:
        raise ValueError(f"不支持的文件格式: {ext}")

    # 生成大纲
    outline = generate_outline(content, input_file)

    # 保存
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(outline, f, ensure_ascii=False, indent=2)

    return outline


def parse_pdf(pdf_path):
    """解析PDF文件（简化版，需要安装pdfplumber）"""
    try:
        import pdfplumber

        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text
    except ImportError:
        # 如果没有pdfplumber，返回提示
        return f"[需要安装pdfplumber] PDF文件: {pdf_path}"


def parse_md(md_path):
    """解析MD文件"""
    with open(md_path, "r", encoding="utf-8") as f:
        return f.read()


def generate_outline(content, source_file):
    """生成结构化大纲"""
    # 提取标题和内容
    lines = content.split("\n")
    sections = []
    current_section = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 检测标题
        title_match = re.match(r"^(#{1,6})\s+(.+)$", line)
        if title_match:
            level = len(title_match.group(1))
            title = title_match.group(2)

            if current_section:
                sections.append(current_section)

            current_section = {
                "level": level,
                "title": title,
                "content": "",
                "key_points": [],
            }
        elif current_section:
            # 收集要点
            if line.startswith("- ") or line.startswith("* "):
                current_section["key_points"].append(line[2:])
            else:
                current_section["content"] += line + "\n"

    if current_section:
        sections.append(current_section)

    # 如果没有检测到标题，创建默认章节
    if not sections:
        sections = [
            {
                "level": 1,
                "title": os.path.basename(source_file),
                "content": content[:500],
                "key_points": content.split("\n")[:5],
            }
        ]

    return {
        "title": os.path.basename(source_file),
        "sections": sections,
        "metadata": {"source": source_file, "sections_count": len(sections)},
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("用法: python -m pdf_parser <输入文件> <输出文件>")
        sys.exit(1)

    parse_document(sys.argv[1], sys.argv[2])
    print(f"解析完成: {sys.argv[2]}")
