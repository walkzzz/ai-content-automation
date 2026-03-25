"""
视频渲染模块 - 优化版
支持两种方案：1. FFmpeg直接生成（推荐，稳定）2. Remotion生成（需要调试）
"""

import os
import json
import shutil
import sys
import subprocess

# 修复Windows控制台编码问题
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass


def render_video_ffmpeg(project_dir, output_file, audio_dir=None):
    """使用FFmpeg直接生成视频（稳定方案）"""
    
    print(f"🎬 使用FFmpeg生成视频...")
    
    # 检查ffmpeg
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
    except:
        print("❌ FFmpeg未安装，请先安装: https://ffmpeg.org/download.html")
        return None
    
    # 获取音频文件
    audio_file = None
    if audio_dir and os.path.exists(audio_dir):
        # 优先使用合并后的音频
        all_audio = os.path.join(audio_dir, "all_audio.mp3")
        if os.path.exists(all_audio):
            audio_file = all_audio
        else:
            # 使用第一个片段
            mp3_files = sorted([f for f in os.listdir(audio_dir) if f.endswith(".mp3")])
            if mp3_files:
                audio_file = os.path.join(audio_dir, mp3_files[0])
    
    # 创建临时目录用于帧
    frames_dir = os.path.join(os.path.dirname(output_file), "temp_frames")
    os.makedirs(frames_dir, exist_ok=True)
    
    # 读取timeline获取时长
    timeline_file = os.path.join(audio_dir, "timeline.json") if audio_dir else None
    duration = 10  # 默认10秒
    if timeline_file and os.path.exists(timeline_file):
        with open(timeline_file, "r") as f:
            timeline = json.load(f)
            duration = timeline.get("total_duration", 10)
    
    # 生成简单背景帧（可以用PPT替换为更好的图片）
    print(f"📊 生成视频帧...")
    generate_simple_frames(frames_dir, duration)
    
    # 构建ffmpeg命令
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    if audio_file:
        # 有音频：视频时长=音频时长
        cmd = f'ffmpeg -y -framerate 1 -i "{frames_dir}/frame_%03d.png" -i "{audio_file}" -c:v libx264 -pix_fmt yuv420p -c:a aac -shortest "{output_file}"'
    else:
        # 无音频
        duration_str = max(duration, 5)
        cmd = f'ffmpeg -y -framerate 1 -i "{frames_dir}/frame_%03d.png" -c:v libx264 -pix_fmt yuv420p -t {duration_str} "{output_file}"'
    
    print(f"🔄 执行: 视频生成...")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0 and os.path.exists(output_file):
        print(f"✅ 视频生成成功: {output_file}")
        
        # 清理临时文件
        shutil.rmtree(frames_dir, ignore_errors=True)
        return output_file
    else:
        print(f"❌ 生成失败: {result.stderr}")
        return None


def generate_simple_frames(frames_dir, duration):
    """生成简单的视频帧（蓝底白字）"""
    # 计算需要多少帧（每秒1帧，每章节1帧）
    num_frames = max(int(duration), 10)
    
    # 章节标题
    titles = [
        "勾股定理可视化证明",
        "一、赵爽弦图证明",
        "二、毕达哥拉斯拼图证明",
        "三、总统伽菲尔德证明",
        "四、面积割补法",
        "五、相似三角形证明",
        "六、动态几何软件演示",
        "七、总结"
    ]
    
    for i in range(num_frames):
        frame_file = os.path.join(frames_dir, f"frame_{i+1:03d}.png")
        
        # 选择标题
        title_idx = min(i // 3, len(titles) - 1)
        title = titles[title_idx]
        
        # 使用ffmpeg生成帧
        color = "#1a1a2e" if i % 2 == 0 else "#16213e"  # 交替背景色
        
        # 创建临时文本文件
        text_file = os.path.join(frames_dir, "text.txt")
        with open(text_file, "w", encoding="utf-8") as f:
            f.write(title)
        
        # 生成单帧图片
        cmd = f'ffmpeg -y -f lavfi -i color=c={color}:s=1920x1080:d=1 -vf "drawtext=textfile=\'{text_file}\':fontcolor=white:fontsize=72:x=(w-text_w)/2:y=(h-text_h)/2" -frames:v 1 "{frame_file}"'
        subprocess.run(cmd, shell=True, capture_output=True)
    
    print(f"📊 已生成 {num_frames} 帧")


def create_project(script_file, audio_dir, project_dir):
    """创建Remotion项目"""
    
    os.makedirs(project_dir, exist_ok=True)
    
    # 创建package.json
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
            "react-dom": "18.2.0"
        }
    }
    
    with open(os.path.join(project_dir, "package.json"), "w", encoding="utf-8") as f:
        json.dump(package_json, f, indent=2)
    
    # 创建src目录
    src_dir = os.path.join(project_dir, "src")
    os.makedirs(src_dir, exist_ok=True)
    
    # 读取脚本内容
    with open(script_file, "r", encoding="utf-8") as f:
        script_content = f.read()
    
    # 生成Video.tsx
    video_tsx = generate_video_tsx(script_content)
    with open(os.path.join(src_dir, "Video.tsx"), "w", encoding="utf-8") as f:
        f.write(video_tsx)
    
    # 复制音频文件
    if audio_dir and os.path.exists(audio_dir):
        public_dir = os.path.join(project_dir, "public")
        os.makedirs(public_dir, exist_ok=True)
        for f in os.listdir(audio_dir):
            if f.endswith(".mp3"):
                shutil.copy2(os.path.join(audio_dir, f), os.path.join(public_dir, f))
    
    print(f"✅ Remotion项目已创建: {project_dir}")
    print(f"📦 请运行: cd {project_dir} && npm install")
    
    return project_dir


def generate_video_tsx(script_content):
    """生成Remotion视频组件"""
    
    # 提取章节
    sections = extract_sections(script_content)
    sections_json = json.dumps(sections)
    
    tsx = f'''import React from "react";
import {{ Composition, AbsoluteFill, Text, registerRoot }} from "remotion";

const sections = {sections_json};

const VideoContent: React.FC = () => {{
  return (
    <AbsoluteFill style={{{{ backgroundColor: "#1a1a2e" }}}>
      {{sections.map((title, index) => (
        <AbsoluteFill
          key={{index}}
          style={{{{
            justifyContent: "center",
            alignItems: "center",
            backgroundColor: index % 2 === 0 ? "#1a1a2e" : "#16213e",
          }}}}
        >
          <Text
            style={{{{
              fontSize: 60,
              color: "white",
              textAlign: "center",
              padding: 40,
            }}}}
          >
            {{title}}
          </Text>
        </AbsoluteFill>
      ))}}
    </AbsoluteFill>
  );
}};

const Root: React.FC = () => {{
  return (
    <>
      <Composition
        id="main-video"
        component={{VideoContent}}
        durationInFrames={{sections.length * 150}}
        fps={{30}}
        width={{1920}}
        height={{1080}}
      />
    </>
  );
}};

registerRoot(Root);
'''
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
    
    # 优先使用FFmpeg方案（更稳定）
    if audio_dir and os.path.exists(audio_dir):
        result = render_video_ffmpeg(project_dir, output_file, audio_dir)
        if result:
            return result
    
    # 降级到Remotion
    print("⚠️ FFmpeg方案不可用，尝试Remotion...")
    return render_video_remotion(project_dir, output_file)


def render_video_remotion(project_dir, output_file):
    """使用Remotion渲染视频"""
    
    print(f"🎬 使用Remotion渲染视频...")
    
    # 检查npm
    try:
        subprocess.run(["npm", "-v"], capture_output=True, check=True)
    except:
        print("❌ Node.js未安装")
        return None
    
    # 安装依赖
    package_json = os.path.join(project_dir, "package.json")
    if not os.path.exists(package_json):
        print("📦 安装依赖...")
        subprocess.run(["npm", "install"], cwd=project_dir, capture_output=True)
    
    # 渲染
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    cmd = f'cd {project_dir} && npx remotion render src/Video.tsx main-video out/video.mp4'
    
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
