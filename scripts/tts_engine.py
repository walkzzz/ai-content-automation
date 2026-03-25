"""
TTS配音生成模块
"""

import os
import json
import asyncio
import re
import sys

# 修复Windows控制台编码问题
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass


async def generate_tts_async(script_file, output_dir, voice="zh-CN-XiaoxiaoNeural"):
    """异步生成TTS配音"""
    os.makedirs(output_dir, exist_ok=True)

    # 读取脚本
    with open(script_file, "r", encoding="utf-8") as f:
        script_content = f.read()

    # 提取旁白内容
    narrations = extract_narrations(script_content)

    # 生成时间轴
    timeline = {"segments": [], "total_duration": 0}

    # 尝试导入edge-tts
    try:
        import edge_tts
    except ImportError:
        print("⚠️ edge-tts 未安装，正在安装...")
        os.system("pip install edge-tts")
        import edge_tts

    # 生成每个片段
    for i, narration in enumerate(narrations):
        if not narration.strip():
            continue

        segment_file = os.path.join(output_dir, f"segment_{i + 1:03d}.mp3")
        srt_file = os.path.join(output_dir, f"segment_{i + 1:03d}.srt")

        print(f"🔊 生成片段 {i + 1}: {narration[:30]}...")

        # 生成语音
        communicate = edge_tts.Communicate(narration, voice)
        await communicate.save(segment_file)

        # 估算时长（简化：每中文字符0.3秒）
        duration = len(narration) * 0.3
        start_time = timeline["total_duration"]
        end_time = start_time + duration

        # 生成SRT字幕
        srt_content = f"{i + 1}\n{format_srt_time(start_time)} --> {format_srt_time(end_time)}\n{narration}\n"
        with open(srt_file, "w", encoding="utf-8") as f:
            f.write(srt_content)

        timeline["segments"].append(
            {
                "id": i + 1,
                "text": narration,
                "start": start_time,
                "end": end_time,
                "audio_file": os.path.basename(segment_file),
                "srt_file": os.path.basename(srt_file),
            }
        )

        timeline["total_duration"] = end_time

    # 保存时间轴
    timeline_file = os.path.join(output_dir, "timeline.json")
    with open(timeline_file, "w", encoding="utf-8") as f:
        json.dump(timeline, f, ensure_ascii=False, indent=2)

    print(f"✅ TTS生成完成，共 {len(timeline['segments'])} 个片段")
    print(f"📁 文件保存在: {output_dir}")

    return timeline


def generate_tts(script_file, output_dir, voice="zh-CN-XiaoxiaoNeural"):
    """同步调用入口"""
    return asyncio.run(generate_tts_async(script_file, output_dir, voice))


def extract_narrations(script_content):
    """从脚本中提取旁白内容"""
    narrations = []

    lines = script_content.split("\n")
    in_narration = False
    current_narration = []

    for line in lines:
        line = line.strip()

        if line.startswith("**旁白**:"):
            in_narration = True
            current_narration.append(line.replace("**旁白**:", "").strip())
        elif line.startswith("## "):
            # 新章节开始，保存之前的旁白
            if current_narration:
                narrations.append(" ".join(current_narration))
                current_narration = []
            in_narration = False
        elif in_narration and line and not line.startswith("**"):
            current_narration.append(line)
        elif line.startswith("- ") or line.startswith("* "):
            # 要点，不作为旁白
            pass

    # 保存最后的旁白
    if current_narration:
        narrations.append(" ".join(current_narration))

    return narrations


def format_srt_time(seconds):
    """格式化SRT时间"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("用法: python -m tts_engine <脚本文件> <输出目录> [音色]")
        sys.exit(1)

    voice = sys.argv[3] if len(sys.argv) > 3 else "zh-CN-XiaoxiaoNeural"
    generate_tts(sys.argv[1], sys.argv[2], voice)
