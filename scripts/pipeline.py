"""
完整流水线执行
"""

import os
import json
import sys


def run_full_pipeline(input_file, output_dir, voice="zh-CN-XiaoxiaoNeural"):
    """执行完整的内容生成流程"""

    print(f"🚀 开始执行完整流水线...")
    print(f"📄 输入文件: {input_file}")
    print(f"📁 输出目录: {output_dir}")
    print("-" * 50)

    # Step 1: 解析文档
    print("\n📝 Step 1: 解析文档...")
    outline_file = os.path.join(output_dir, "outline.json")
    from .pdf_parser import parse_document

    parse_document(input_file, outline_file)
    print(f"✅ 大纲已保存到: {outline_file}")

    # Step 2: 生成脚本
    print("\n📝 Step 2: 生成视频脚本...")
    script_file = os.path.join(output_dir, "script.md")
    from .script_generator import generate_script

    generate_script(outline_file, script_file)
    print(f"✅ 脚本已保存到: {script_file}")

    # Step 3: 生成TTS配音
    print("\n📝 Step 3: 生成TTS配音...")
    audio_dir = os.path.join(output_dir, "audio")
    os.makedirs(audio_dir, exist_ok=True)
    from .tts_engine import generate_tts

    generate_tts(script_file, audio_dir, voice)
    print(f"✅ 配音已保存到: {audio_dir}")

    # Step 4: 创建Remotion项目
    print("\n📝 Step 4: 创建Remotion项目...")
    project_dir = os.path.join(output_dir, "remotion-project")
    from .remotion_render import create_project

    create_project(script_file, audio_dir, project_dir)
    print(f"✅ Remotion项目已创建: {project_dir}")

    # Step 5: 渲染视频（自动合并配音）
    print("\n📝 Step 5: 渲染视频...")
    video_file = os.path.join(output_dir, "videos", "final.mp4")
    os.makedirs(os.path.dirname(video_file), exist_ok=True)
    from .remotion_render import render_video

    render_video(project_dir, video_file, audio_dir)
    print(f"✅ 视频已渲染: {video_file}")

    print("\n" + "=" * 50)
    print(f"🎉 流水线执行完成！")
    print(f"📹 视频位置: {video_file}")
    print("=" * 50)
