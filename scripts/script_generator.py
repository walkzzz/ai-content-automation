"""
视频脚本生成模块
"""

import json
import os


def generate_script(outline_file, output_file):
    """基于大纲生成视频脚本"""

    # 读取大纲
    with open(outline_file, "r", encoding="utf-8") as f:
        outline = json.load(f)

    script_lines = []

    # 标题
    script_lines.append(f"# {outline.get('title', '视频脚本')}")
    script_lines.append("")
    script_lines.append("---")
    script_lines.append("")

    # 生成每个章节的脚本
    for i, section in enumerate(outline.get("sections", [])):
        title = section.get("title", "")
        level = section.get("level", 1)
        content = section.get("content", "").strip()
        key_points = section.get("key_points", [])

        # 章节标题
        script_lines.append(f"## 第{i + 1}部分: {title}")
        script_lines.append("")

        # 旁白内容
        if content:
            # 简化内容，生成旁白
            narration = content[:200] if len(content) > 200 else content
            script_lines.append(f"**旁白**: {narration}")
            script_lines.append("")

        # 要点
        if key_points:
            script_lines.append("**要点**:")
            for point in key_points[:3]:
                script_lines.append(f"- {point}")
            script_lines.append("")

        # 时间估算（简化：每章节约30秒）
        script_lines.append(f"⏱ 时长: 约30秒")
        script_lines.append("")
        script_lines.append("---")
        script_lines.append("")

    # 添加总结
    script_lines.append("## 视频信息")
    script_lines.append("")
    script_lines.append(f"- 总章节数: {len(outline.get('sections', []))}")
    script_lines.append(f"- 预计总时长: {len(outline.get('sections', [])) * 30} 秒")
    script_lines.append("")

    # 保存
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(script_lines))

    return output_file


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("用法: python -m script_generator <大纲文件> <输出脚本>")
        sys.exit(1)

    generate_script(sys.argv[1], sys.argv[2])
    print(f"脚本生成完成: {sys.argv[2]}")
