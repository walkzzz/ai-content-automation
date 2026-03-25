"""
视频渲染模块 - 完整版
支持从timeline.json读取每个片段，生成对应的幻灯片视频
"""

import os
import json
import shutil
import sys
import subprocess

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass


def get_segment_texts(timeline_file):
    """从timeline.json读取每个片段的文本"""
    if not timeline_file or not os.path.exists(timeline_file):
        return None

    with open(timeline_file, "r", encoding="utf-8") as f:
        timeline = json.load(f)

    segments = timeline.get("segments", [])
    texts = []
    for seg in segments:
        text = seg.get("text", "")[:100]  # 截取前100字
        texts.append(text)
    return texts


def generate_slide_frames(frames_dir, segment_texts, segment_durations):
    """为每个片段生成一张幻灯片"""
    os.makedirs(frames_dir, exist_ok=True)

    colors = ["#1a1a2e", "#16213e", "#0f3460", "#1a1a2e", "#16213e"]

    for i, text in enumerate(segment_texts):
        frame_file = os.path.join(frames_dir, f"frame_{i + 1:04d}.png")

        # 简化文本用于显示（取前50字，加换行）
        display_text = text[:50]
        if len(text) > 50:
            display_text = text[:25] + "\n" + text[25:50]

        # 使用PIL生成图片（更稳定）
        try:
            from PIL import Image, ImageDraw, ImageFont

            # 创建1080p图片
            img = Image.new("RGB", (1920, 1080), color=colors[i % len(colors)])
            draw = ImageDraw.Draw(img)

            # 尝试加载字体
            try:
                font = ImageFont.truetype("arial.ttf", 60)
                small_font = ImageFont.truetype("arial.ttf", 36)
            except:
                font = ImageFont.load_default()
                small_font = ImageFont.load_default()

            # 绘制标题
            title = f"第{i + 1}节"
            draw.text((100, 100), title, font=font, fill="white")

            # 绘制内容（多行）
            y = 250
            for line in display_text.split("\n"):
                draw.text((100, y), line, font=small_font, fill="white")
                y += 60

            # 保存
            img.save(frame_file)
            print(f"  ✓ 生成帧 {i + 1}/{len(segment_texts)}")

        except ImportError:
            # 如果没有PIL，使用ffmpeg
            color = colors[i % len(colors)].replace("#", "")
            # 转换颜色格式
            r = int(color[0:2], 16)
            g = int(color[2:4], 16)
            b = int(color[4:6], 16)

            text_file = os.path.join(frames_dir, f"text_{i}.txt")
            with open(text_file, "w", encoding="utf-8") as f:
                f.write(display_text.replace("\n", " "))

            cmd = f'ffmpeg -y -f lavfi -i color=c=0x{color}:s=1920x1080:d=1 -vf "drawtext=textfile=\'{text_file}\':fontcolor=white:fontsize=48:x=100:y=200" -frames:v 1 "{frame_file}"'
            subprocess.run(cmd, shell=True, capture_output=True)

    return len(segment_texts)


def render_video_ffmpeg(project_dir, output_file, audio_dir=None):
    """使用FFmpeg生成视频（稳定方案）"""

    print(f"🎬 使用FFmpeg生成视频...")

    # 检查ffmpeg
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception("FFmpeg not found")
    except:
        print("❌ FFmpeg未安装，请先安装: https://ffmpeg.org/download.html")
        return None

    # 获取音频文件和timeline
    audio_file = None
    timeline_file = None
    if audio_dir and os.path.exists(audio_dir):
        all_audio = os.path.join(audio_dir, "all_audio.mp3")
        if os.path.exists(all_audio):
            audio_file = all_audio
        timeline_file = os.path.join(audio_dir, "timeline.json")

    # 读取timeline获取片段信息
    segment_texts = None
    segment_durations = []
    if timeline_file and os.path.exists(timeline_file):
        with open(timeline_file, "r", encoding="utf-8") as f:
            timeline = json.load(f)
        segments = timeline.get("segments", [])
        segment_texts = [
            seg.get("text", f"第{i + 1}节")[:80] for i, seg in enumerate(segments)
        ]
        segment_durations = [
            seg.get("end", 0) - seg.get("start", 0) for seg in segments
        ]

    # 创建临时帧目录
    frames_dir = os.path.join(os.path.dirname(output_file), "temp_frames")
    if os.path.exists(frames_dir):
        shutil.rmtree(frames_dir)
    os.makedirs(frames_dir, exist_ok=True)

    # 生成帧
    print(f"📊 生成视频帧...")
    if segment_texts:
        num_frames = generate_slide_frames(frames_dir, segment_texts, segment_durations)
    else:
        # 回退：生成默认帧
        num_frames = generate_simple_frames(frames_dir)

    if num_frames == 0:
        print("❌ 帧生成失败")
        return None

    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # 构建ffmpeg命令
    # 使用concat demuxer来精确控制每帧的显示时长
    if audio_file and os.path.exists(audio_file):
        # 获取音频时长
        probe_cmd = f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{audio_file}"'
        result = subprocess.run(probe_cmd, shell=True, capture_output=True, text=True)
        audio_duration = float(result.stdout.strip()) if result.stdout.strip() else 30

        # 计算每帧显示时长 = 总音频时长 / 帧数
        frame_duration = audio_duration / num_frames if num_frames > 0 else 1

        print(f"   音频时长: {audio_duration:.1f}秒, 每帧显示: {frame_duration:.1f}秒")

        # 创建concat文件
        concat_file = os.path.join(frames_dir, "concat.txt")
        with open(concat_file, "w") as f:
            for i in range(1, num_frames + 1):
                frame_file = os.path.join(frames_dir, f"frame_{i:04d}.png")
                if os.path.exists(frame_file):
                    f.write(f"file '{frame_file}'\n")
                    f.write(f"duration {frame_duration}\n")

        # 最后再加一次最后一帧，确保视频完整
        last_frame = os.path.join(frames_dir, f"frame_{num_frames:04d}.png")
        if os.path.exists(last_frame):
            with open(concat_file, "a") as f:
                f.write(f"file '{last_frame}'\n")

        # 使用concat demuxer合并
        cmd = f'ffmpeg -y -f concat -safe 0 -i "{concat_file}" -i "{audio_file}" -c:v libx264 -pix_fmt yuv420p -c:a aac -shortest -vsync vfr "{output_file}"'
    else:
        # 无音频
        frame_pattern = os.path.join(frames_dir, "frame_%04d.png")
        cmd = f'ffmpeg -y -framerate 1 -i "{frame_pattern}" -c:v libx264 -pix_fmt yuv420p -t {num_frames * 2} "{output_file}"'

    print(f"🔄 执行视频合成...")

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"❌ 视频合成失败: {result.stderr[-500:]}")
        # 尝试简化命令
        print("   尝试简化方案...")
        return render_video_simple(frames_dir, output_file, audio_file)

    if os.path.exists(output_file) and os.path.getsize(output_file) > 1000:
        print(f"✅ 视频生成成功: {output_file}")
        file_size = os.path.getsize(output_file) / 1024 / 1024
        print(f"   文件大小: {file_size:.2f} MB")

        # 清理临时文件
        shutil.rmtree(frames_dir, ignore_errors=True)
        return output_file
    else:
        print(f"❌ 视频文件无效")
        return render_video_simple(frames_dir, output_file, audio_file)


def render_video_simple(frames_dir, output_file, audio_file):
    """简化版视频生成"""
    print("   使用简化方案...")

    # 获取所有帧
    frames = sorted([f for f in os.listdir(frames_dir) if f.endswith(".png")])
    if not frames:
        print("❌ 没有帧文件")
        return None

    # 创建concat列表
    concat_file = os.path.join(frames_dir, "concat.txt")
    with open(concat_file, "w") as f:
        for frame in frames:
            f.write(f"file '{os.path.join(frames_dir, frame)}'\n")
            f.write(f"duration 3\n")
        # 最后再加一次
        f.write(f"file '{os.path.join(frames_dir, frames[-1])}'\n")

    if audio_file and os.path.exists(audio_file):
        cmd = f'ffmpeg -y -f concat -safe 0 -i "{concat_file}" -i "{audio_file}" -c:v libx264 -pix_fmt yuv420p -c:a aac -shortest "{output_file}"'
    else:
        cmd = f'ffmpeg -y -f concat -safe 0 -i "{concat_file}" -c:v libx264 -pix_fmt yuv420p "{output_file}"'

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode == 0 and os.path.exists(output_file):
        print(f"✅ 简化方案成功: {output_file}")
        return output_file
    else:
        print(f"❌ 简化方案失败: {result.stderr[-300:]}")
        return None


def generate_simple_frames(frames_dir):
    """生成简单的默认帧（回退方案）"""
    titles = [
        "勾股定理可视化证明",
        "赵爽弦图证明",
        "毕达哥拉斯拼图",
        "总统伽菲尔德证明",
        "面积割补法",
        "相似三角形证明",
        "动态几何演示",
        "总结",
    ]

    num_frames = len(titles)
    colors = ["#1a1a2e", "#16213e", "#0f3460"]

    try:
        from PIL import Image, ImageDraw, ImageFont

        for i, title in enumerate(titles):
            frame_file = os.path.join(frames_dir, f"frame_{i + 1:04d}.png")
            img = Image.new("RGB", (1920, 1080), color=colors[i % len(colors)])
            draw = ImageDraw.Draw(img)

            try:
                font = ImageFont.truetype("arial.ttf", 72)
            except:
                font = ImageFont.load_default()

            draw.text((960, 540), title, font=font, fill="white", anchor="mm")
            img.save(frame_file)

        return num_frames

    except ImportError:
        # 使用ffmpeg
        for i, title in enumerate(titles):
            frame_file = os.path.join(frames_dir, f"frame_{i + 1:04d}.png")
            color = colors[i % len(colors)].replace("#", "")
            text_file = os.path.join(frames_dir, "text.txt")
            with open(text_file, "w", encoding="utf-8") as f:
                f.write(title)
            cmd = f'ffmpeg -y -f lavfi -i color=c=0x{color}:s=1920x1080:d=1 -vf "drawtext=textfile=\'{text_file}\':fontcolor=white:fontsize=72:x=(w-text_w)/2:y=(h-text_h)/2" -frames:v 1 "{frame_file}"'
            subprocess.run(cmd, shell=True, capture_output=True)

        return num_frames


def create_project(script_file, audio_dir, project_dir):
    """创建Remotion项目"""

    os.makedirs(project_dir, exist_ok=True)

    package_json = {
        "name": "ai-content-video",
        "version": "1.0.0",
        "description": "AI生成的视频项目",
        "scripts": {
            "start": "remotion studio",
            "build": "remotion render src/Video.tsx main-video out/video.mp4",
        },
        "dependencies": {
            "@remotion/cli": "4.0.0",
            "remotion": "4.0.0",
            "react": "18.2.0",
            "react-dom": "18.2.0",
        },
    }

    with open(os.path.join(project_dir, "package.json"), "w", encoding="utf-8") as f:
        json.dump(package_json, f, indent=2)

    src_dir = os.path.join(project_dir, "src")
    os.makedirs(src_dir, exist_ok=True)

    with open(script_file, "r", encoding="utf-8") as f:
        script_content = f.read()

    video_tsx = generate_video_tsx(script_content)
    with open(os.path.join(src_dir, "Video.tsx"), "w", encoding="utf-8") as f:
        f.write(video_tsx)

    if audio_dir and os.path.exists(audio_dir):
        public_dir = os.path.join(project_dir, "public")
        os.makedirs(public_dir, exist_ok=True)
        for f in os.listdir(audio_dir):
            if f.endswith(".mp3"):
                shutil.copy2(os.path.join(audio_dir, f), os.path.join(public_dir, f))

    print(f"✅ Remotion项目已创建: {project_dir}")
    return project_dir


def generate_video_tsx(script_content):
    """生成Remotion视频组件"""

    sections = extract_sections(script_content)
    sections_json = json.dumps(sections)

    tsx = (
        """import React from "react";
import { Composition, AbsoluteFill, Text, registerRoot } from "remotion";

const sections = """
        + sections_json
        + """;

const VideoContent: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: "#1a1a2e" }}>
      {sections.map((title, index) => (
        <AbsoluteFill
          key={index}
          style={{
            justifyContent: "center",
            alignItems: "center",
            backgroundColor: index % 2 === 0 ? "#1a1a2e" : "#16213e",
          }}
        >
          <Text
            style={{
              fontSize: 60,
              color: "white",
              textAlign: "center",
              padding: 40,
            }}
          >
            {title}
          </Text>
        </AbsoluteFill>
      ))}
    </AbsoluteFill>
  );
};

const Root: React.FC = () => {
  return (
    <>
      <Composition
        id="main-video"
        component={VideoContent}
        durationInFrames={sections.length * 150}
        fps={30}
        width={1920}
        height={1080}
      />
    </>
  );
};

registerRoot(Root);
"""
    )
    return tsx


def extract_sections(script_content):
    """从脚本提取章节标题"""
    sections = []
    lines = script_content.split("\n")
    for line in lines:
        if line.startswith("## 第") and "章" in line:
            title = line.replace("## 第", "").replace("章:", "").strip()
            sections.append(title)
    return sections if sections else ["AI Generated Video"]


def render_video(project_dir, output_file, audio_dir=None):
    """渲染视频主函数 - 优先使用FFmpeg"""

    if audio_dir and os.path.exists(audio_dir):
        result = render_video_ffmpeg(project_dir, output_file, audio_dir)
        if result:
            return result

    print("⚠️ FFmpeg方案不可用，尝试Remotion...")
    return render_video_remotion(project_dir, output_file)


def render_video_remotion(project_dir, output_file):
    """使用Remotion渲染视频"""

    print(f"🎬 使用Remotion渲染视频...")

    try:
        subprocess.run(["npm", "-v"], capture_output=True, check=True)
    except:
        print("❌ Node.js未安装")
        return None

    package_json = os.path.join(project_dir, "package.json")
    if not os.path.exists(package_json):
        print("📦 安装依赖...")
        subprocess.run(["npm", "install"], cwd=project_dir, capture_output=True)

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    cmd = f"cd {project_dir} && npx remotion render src/Video.tsx main-video out/video.mp4"

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        out_video = os.path.join(project_dir, "out", "video.mp4")
        if os.path.exists(out_video):
            shutil.copy2(out_video, output_file)
            return output_file

    print(f"❌ Remotion渲染失败: {result.stderr[-500:]}")
    return None


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="视频渲染")
    parser.add_argument("project", help="项目目录")
    parser.add_argument("output", help="输出视频")
    parser.add_argument("--audio", help="音频目录")

    args = parser.parse_args()

    render_video(args.project, args.output, args.audio)
