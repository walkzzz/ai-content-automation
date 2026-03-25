"""
Remotion视频渲染模块
"""

import os
import json
import shutil
import sys

# 修复Windows控制台编码问题
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass


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
            "build": "remotion render src/Video.tsx out video.mp4",
            "preview": "remotion preview src/Video.tsx",
        },
        "dependencies": {
            "@remotion/cli": "^4.0.0",
            "@remotion/node": "^4.0.0",
            "@remotion/react": "^4.0.0",
            "react": "^18.2.0",
            "react-dom": "^18.2.0",
        },
    }

    with open(os.path.join(project_dir, "package.json"), "w", encoding="utf-8") as f:
        json.dump(package_json, f, indent=2)

    # 创建remotion.config.ts
    config_ts = """import { Config } from "@remotion/cli";

Config.setVideoImageFormat("png");
Config.setCodec("h264");
"""

    with open(
        os.path.join(project_dir, "remotion.config.ts"), "w", encoding="utf-8"
    ) as f:
        f.write(config_ts)

    # 创建src目录
    src_dir = os.path.join(project_dir, "src")
    os.makedirs(src_dir, exist_ok=True)

    # 读取脚本内容
    with open(script_file, "r", encoding="utf-8") as f:
        script_content = f.read()

    # 生成Video.tsx
    video_tsx = generate_video_tsx(script_content, audio_dir)
    with open(os.path.join(src_dir, "Video.tsx"), "w", encoding="utf-8") as f:
        f.write(video_tsx)

    # 生成index.tsx
    index_tsx = """import { render } from "@remotion/node";
import { Video } from "./Video";

render(Video, { outPath: "out/video.mp4" });
"""
    with open(os.path.join(src_dir, "index.tsx"), "w", encoding="utf-8") as f:
        f.write(index_tsx)

    # 复制音频文件
    audio_dest = os.path.join(src_dir, "audio")
    if os.path.exists(audio_dir):
        os.makedirs(audio_dest, exist_ok=True)
        for f in os.listdir(audio_dir):
            if f.endswith(".mp3"):
                shutil.copy2(os.path.join(audio_dir, f), os.path.join(audio_dest, f))

    print(f"✅ Remotion项目已创建: {project_dir}")
    print(f"📦 请运行: cd {project_dir} && npm install")
    print(
        f"🎬 渲染视频: cd {project_dir} && npx remotion render src/Video.tsx out video.mp4"
    )

    return project_dir


def generate_video_tsx(script_content, audio_dir):
    """生成Remotion视频组件"""

    # 提取章节信息
    sections = []
    lines = script_content.split("\n")
    for line in lines:
        if line.startswith("## 第"):
            # 提取章节标题
            title = line.replace("## 第", "").replace("部分:", "").strip()
            sections.append(title)

    if not sections:
        sections = ["AI Generated Content"]

    # 生成TSX代码
    sections_json = json.dumps(sections)

    tsx = (
        """import { useCurrentFrame, useVideoConfig, interpolate, AbsoluteFill, Audio, staticFile, Text } from "@remotion/node";
import { composition } from "@remotion/react";
import React from "react";

const sections_json = """
        + sections_json
        + """;

const Video = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  return (
    <AbsoluteFill style={{ backgroundColor: "#1a1a2e" }}>
      {sections_json.map((title, index) => (
        <Slide 
          key={index} 
          title={title} 
          startFrame={index * 150}
          duration={150}
        />
      ))}
      
      <Audio src={staticFile("audio/segment_001.mp3")} />
    </AbsoluteFill>
  );
};

const Slide = ({ title, startFrame, duration }) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(
    frame,
    [startFrame, startFrame + 30, startFrame + duration - 30, startFrame + duration],
    [0, 1, 1, 0]
  );

  return (
    <AbsoluteFill style={{ opacity, justifyContent: "center", alignItems: "center" }}>
      <Text style={{ fontSize: 60, color: "white", textAlign: "center" }}>
        {title}
      </Text>
    </AbsoluteFill>
  );
};

export const VideoComposition = composition({
  id: "Video",
  component: Video,
  durationInFrames: 600,
  fps: 30,
});

export default Video;
"""
    )

    return tsx


def render_video(project_dir, output_file):
    """渲染视频"""

    print(f"🎬 开始渲染视频...")
    print(f"📁 项目目录: {project_dir}")
    print(f"📹 输出文件: {output_file}")

    # 检查依赖
    package_json = os.path.join(project_dir, "package.json")
    if not os.path.exists(package_json):
        print("⚠️ 依赖未安装，正在安装...")
        os.system(f"cd {project_dir} && npm install")

    # 执行渲染
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # 简化版：检查ffmpeg是否可用
    ffmpeg_check = os.system("where ffmpeg >nul 2>&1")

    if ffmpeg_check == 0:
        print("✅ ffmpeg 已安装")
        # 如果有Remotion输出，直接使用
        out_video = os.path.join(project_dir, "out", "video.mp4")
        if os.path.exists(out_video):
            shutil.copy2(out_video, output_file)
            print(f"✅ 视频渲染完成: {output_file}")
        else:
            print(
                "⚠️ 请先运行: cd {} && npx remotion render src/Video.tsx out video.mp4".format(
                    project_dir
                )
            )
    else:
        print("⚠️ ffmpeg 未安装，请先安装 ffmpeg")
        print("💡 安装地址: https://ffmpeg.org/download.html")

    return output_file


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("用法: python -m remotion_render <项目目录> <输出视频>")
        sys.exit(1)

    render_video(sys.argv[1], sys.argv[2])
