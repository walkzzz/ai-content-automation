"""
TTS配音生成模块 - 优化版
支持多种声音，更好的错误处理
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


# 可用的语音列表
VOICES = {
    # 中文
    "zh-CN-XiaoxiaoNeural": "晓晓 - 通用女声",
    "zh-CN-YunxiNeural": "云希 - 通用男声",
    "zh-CN-XiaoyiNeural": "晓伊 - 活泼女声",
    "zh-CN-YunyangNeural": "云扬 - 专业男声",
    "zh-CN-XiaomoNeural": "晓墨 - 成熟女声",
    "zh-CN-YunhaoNeural": "云浩 - 成熟男声",
    "zh-CN-XiaoxuanNeural": "晓萱 - 温柔女声",
    "zh-CN-YunjiNeural": "云玑 - 学术男声",
    # 英文
    "en-US-JennyNeural": "Jenny - 通用女声",
    "en-US-GuyNeural": "Guy - 通用男声",
    "en-US-AriaNeural": "Aria - 活泼女声",
}


async def generate_tts_async(script_file, output_dir, voice="zh-CN-XiaoxiaoNeural"):
    """异步生成TTS配音"""
    os.makedirs(output_dir, exist_ok=True)

    # 读取脚本
    with open(script_file, "r", encoding="utf-8") as f:
        script_content = f.read()

    # 提取旁白内容
    narrations = extract_narrations(script_content)

    if not narrations:
        print("⚠️ 未找到旁白内容，请检查脚本格式")
        return None

    # 生成时间轴
    timeline = {"segments": [], "total_duration": 0, "voice": voice}

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

        print(f"🔊 生成片段 {i + 1}/{len(narrations)}...")

        # 生成语音
        try:
            communicate = edge_tts.Communicate(narration, voice)
            await communicate.save(segment_file)
        except Exception as e:
            print(f"⚠️ 生成失败: {e}")
            continue

        # 估算时长（中文每字约0.3秒，英文约0.2秒）
        if "zh-CN" in voice:
            duration = len(narration) * 0.35
        else:
            duration = len(narration) * 0.2

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
                "start": round(start_time, 2),
                "end": round(end_time, 2),
                "audio_file": os.path.basename(segment_file),
                "srt_file": os.path.basename(srt_file),
            }
        )

        timeline["total_duration"] = round(end_time, 2)

    # 保存时间轴
    timeline_file = os.path.join(output_dir, "timeline.json")
    with open(timeline_file, "w", encoding="utf-8") as f:
        json.dump(timeline, f, ensure_ascii=False, indent=2)

    # 合并所有音频
    if len(timeline["segments"]) > 1:
        merge_audio_files(output_dir)

    print(f"✅ TTS生成完成，共 {len(timeline['segments'])} 个片段")
    print(f"📁 文件保存在: {output_dir}")
    print(f"⏱ 总时长: {timeline['total_duration']} 秒")

    return timeline


def merge_audio_files(output_dir):
    """合并所有音频片段"""
    import subprocess

    # 查找所有MP3文件
    mp3_files = sorted([f for f in os.listdir(output_dir) if f.endswith(".mp3")])

    if len(mp3_files) < 2:
        return

    # 创建合并列表
    concat_file = os.path.join(output_dir, "concat_list.txt")
    with open(concat_file, "w", encoding="utf-8") as f:
        for mp3 in mp3_files:
            f.write(f"file '{mp3}'\n")

    # 使用ffmpeg合并
    output_file = os.path.join(output_dir, "all_audio.mp3")
    cmd = f'ffmpeg -y -f concat -safe 0 -i "{concat_file}" -c copy "{output_file}"'

    try:
        subprocess.run(cmd, shell=True, check=True, capture_output=True)
        print(f"✅ 音频已合并: {output_file}")
    except:
        print("⚠️ 音频合并失败")


def generate_tts(script_file, output_dir, voice="zh-CN-XiaoxiaoNeural"):
    """同步调用入口"""
    return asyncio.run(generate_tts_async(script_file, output_dir, voice))


def extract_narrations(script_content):
    """从脚本中提取旁白内容 - 优化版"""
    narrations = []

    lines = script_content.split("\n")
    current_narration = []
    in_narration = False

    for line in lines:
        line = line.strip()

        # 检测TTS旁白标记
        if "**TTS**:" in line or "**旁白**:" in line:
            # 保存之前的旁白
            if current_narration:
                narrations.append(" ".join(current_narration))
                current_narration = []

            # 提取旁白文本
            narration_text = (
                line.replace("**TTS**:", "").replace("**旁白**:", "").strip()
            )
            if narration_text:
                current_narration.append(narration_text)
            in_narration = True

        elif in_narration:
            # 继续收集旁白内容
            if (
                line
                and not line.startswith("**")
                and not line.startswith("#")
                and not line.startswith("-")
            ):
                current_narration.append(line)
            elif line.startswith("##") or line.startswith("---"):
                # 新章节开始
                if current_narration:
                    narrations.append(" ".join(current_narration))
                    current_narration = []
                in_narration = False

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


def list_voices():
    """列出所有可用语音"""
    print("可用语音:")
    for voice_id, desc in VOICES.items():
        print(f"  {voice_id}: {desc}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="TTS配音生成")
    parser.add_argument("script", help="脚本文件")
    parser.add_argument("output", help="输出目录")
    parser.add_argument(
        "-v", "--voice", default="zh-CN-XiaoxiaoNeural", help="语音选择"
    )
    parser.add_argument("--list", action="store_true", help="列出所有可用语音")

    args = parser.parse_args()

    if args.list:
        list_voices()
    else:
        generate_tts(args.script, args.output, args.voice)
