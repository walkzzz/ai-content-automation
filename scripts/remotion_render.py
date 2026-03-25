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

    # 创建package.json - 使用稳定版本3.3.x
    package_json = {
        "name": "ai-content-video",
        "version": "1.0.0",
        "description": "AI生成的视频项目",
        "scripts": {
            "start": "remotion studio",
            "build": "remotion render src/Video.tsx main-video out/video.mp4",
            "preview": "remotion preview src/Video.tsx",
        },
        "dependencies": {
            "@remotion/cli": "3.3.103",
            "remotion": "3.3.103",
            "react": "18.2.0",
            "react-dom": "18.2.0",
        },
    }

    with open(os.path.join(project_dir, "package.json"), "w", encoding="utf-8") as f:
        json.dump(package_json, f, indent=2)

    # 创建tsconfig.json
    tsconfig = {
        "compilerOptions": {
            "target": "ES2020",
            "module": "ESNext",
            "moduleResolution": "node",
            "esModuleInterop": True,
            "jsx": "react-jsx",
            "strict": True,
            "skipLibCheck": True,
            "resolveJsonModule": True,
            "allowSyntheticDefaultImports": True,
        },
        "include": ["src/**/*"],
    }
    with open(os.path.join(project_dir, "tsconfig.json"), "w", encoding="utf-8") as f:
        json.dump(tsconfig, f, indent=2)

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

    # 复制音频文件到public目录
    public_dir = os.path.join(project_dir, "public")
    if os.path.exists(audio_dir):
        os.makedirs(public_dir, exist_ok=True)
        for f in os.listdir(audio_dir):
            if f.endswith(".mp3"):
                shutil.copy2(os.path.join(audio_dir, f), os.path.join(public_dir, f))

    print(f"✅ Remotion项目已创建: {project_dir}")
    print(f"📦 请运行: cd {project_dir} && npm install")
    print(
        f"🎬 渲染视频: cd {project_dir} && npx remotion render src/Video.tsx main-video out/video.mp4"
    )

    return project_dir


def generate_video_tsx(script_content):
    """生成Remotion视频组件 - 使用v3.3兼容API"""

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

    # 生成TSX代码 - 使用v3.3兼容格式
    sections_json = json.dumps(sections)

    tsx = f"""import React from "react";
import {{ Composition, AbsoluteFill, Text, registerRoot }} from "remotion";

const sections = {sections_json};

const VideoContent: React.FC = () => {{
  return (
    <AbsoluteFill style={{{{ backgroundColor: "#1a1a2e" }}}}>
      {{sections.map((title, index) => (
        <AbsoluteFill
          key={{index}}
          style={{{{
            justifyContent: "center",
            alignItems: "center",
            backgroundColor: "#1a1a2e",
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
"""

    return tsx


def render_video(project_dir, output_file):
    """渲染视频"""

    print(f"🎬 开始渲染视频...")
    print(f"📁 项目目录: {project_dir}")
    print(f"📹 输出文件: {output_file}")

    # 检查依赖
    package_json_path = os.path.join(project_dir, "package.json")
    if not os.path.exists(package_json_path):
        print("⚠️ 依赖未安装，正在安装...")
        os.system(f"cd {project_dir} && npm install")

    # 执行渲染
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # 渲染命令
    render_cmd = f"cd {project_dir} && npx remotion render src/Video.tsx main-video out/video.mp4"
    print(f"🔄 执行渲染命令: {render_cmd}")

    result = os.system(render_cmd)

    if result == 0:
        out_video = os.path.join(project_dir, "out", "video.mp4")
        if os.path.exists(out_video):
            shutil.copy2(out_video, output_file)
            print(f"✅ 视频渲染完成: {output_file}")
    else:
        print("⚠️ 渲染失败，请手动检查")

    return output_file


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("用法: python -m remotion_render <项目目录> <输出视频>")
        sys.exit(1)

    render_video(sys.argv[1], sys.argv[2])
