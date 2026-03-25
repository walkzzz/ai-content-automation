"""
视频脚本生成模块 - 优化版
"""

import json
import os
import re


def clean_text_for_tts(text):
    """清理文本，移除Markdown格式，使TTS朗读更自然"""
    if not text:
        return ""

    # 移除LaTeX/数学公式
    text = re.sub(r"\$.*?\$", "", text)
    text = re.sub(r"\\\(.*?\\\)", "", text)
    text = re.sub(r"\\\[.*?\\\]", "", text)

    # 移除代码块
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    text = re.sub(r"`.*?`", "", text)

    # 移除Markdown格式符号
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)  # **粗体**
    text = re.sub(r"\*([^*]+)\*", r"\1", text)  # *斜体*
    text = re.sub(r"__([^_]+)__", r"\1", text)  # __下划线__
    text = re.sub(r"#+\s*", "", text)  # 标题符号
    text = re.sub(r"-\s+", "", text)  # 列表符号
    text = re.sub(r"\d+\.\s+", "", text)  # 数字列表
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)  # 链接

    # 移除多余空白
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" {2,}", " ", text)

    return text.strip()


def generate_script(outline_file, output_file):
    """基于大纲生成更自然的视频脚本"""

    # 读取大纲
    with open(outline_file, "r", encoding="utf-8") as f:
        outline = json.load(f)

    script_lines = []
    sections = outline.get("sections", [])

    # 标题
    title = outline.get("title", "视频脚本")
    script_lines.append(f"# {title}")
    script_lines.append("")

    # 生成每个章节的脚本
    for i, section in enumerate(sections):
        title = section.get("title", "")
        level = section.get("level", 1)
        content = section.get("content", "").strip()
        key_points = section.get("key_points", [])

        # 章节标题（用于视频显示）
        script_lines.append(f"## 第{i + 1}章: {title}")
        script_lines.append("")

        # 旁白内容 - 清理后用于TTS
        if content:
            # 清理Markdown格式
            clean_content = clean_text_for_tts(content)
            # 截取合适长度（每段约100字）
            if len(clean_content) > 150:
                # 在句号处截断
                parts = clean_content.split("。")
                narration = ""
                for part in parts:
                    if len(narration) + len(part) + 1 > 150:
                        break
                    narration += part + "。"
            else:
                narration = clean_content

            if narration:
                script_lines.append(f"**TTS**: {narration}")
                script_lines.append("")

        # 要点（用于视频显示）
        if key_points:
            script_lines.append("**要点**:")
            for point in key_points[:3]:
                clean_point = clean_text_for_tts(point)
                if clean_point:
                    script_lines.append(f"- {clean_point}")
            script_lines.append("")

        # 时间估算
        script_lines.append(f"⏱ 时长: 约{narration_length(narration)}秒")
        script_lines.append("")
        script_lines.append("---")
        script_lines.append("")

    # 添加总结
    script_lines.append("## 总结")
    script_lines.append("")
    script_lines.append(
        f"本视频共 {len(sections)} 个章节，总时长约 {sum_section_durations(sections)} 秒。"
    )
    script_lines.append("")

    # 保存
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(script_lines))

    return output_file


def narration_length(text):
    """估算TTS朗读时长（中文每字约0.3秒）"""
    if not text:
        return 30
    return max(10, min(len(text) // 3, 60))


def sum_section_durations(sections):
    """计算总时长"""
    total = 0
    for section in sections:
        content = section.get("content", "")
        total += narration_length(clean_text_for_tts(content))
    return max(total, 60)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("用法: python -m script_generator <大纲文件> <输出脚本>")
        sys.exit(1)

    generate_script(sys.argv[1], sys.argv[2])
    print(f"脚本生成完成: {sys.argv[2]}")
