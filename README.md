# AI Content Automation

> 从 PDF/MD 文档一键生成完整视频（配音+画面）

## 概述

AI Content Automation 是一个自动化内容生产工具，集成 PDF 解析、视频渲染（Remotion）、TTS 配音、GitHub 归档四大能力，实现从文档到视频的全流程自动化。

## 功能特性

| 模块 | 功能 |
|------|------|
| **PDF解析** | 提取 PDF/MD 内容，生成结构化大纲 |
| **视频渲染** | 使用 Remotion 生成视频代码并渲染 |
| **TTS配音** | 文本转语音，自动同步时间轴 |
| **GitHub归档** | 自动提交代码到 GitHub 仓库 |

## 快速开始

### 1. 安装依赖

```bash
# 克隆或复制 skill 到本地
cd ai-content-automation

# 安装 Python 依赖
pip install -r requirements.txt

# 安装 Node.js 依赖（首次创建项目时自动安装）
npm install
```

### 2. 一键执行完整流程

```bash
# 基本用法
python -m ai_content_automation run -i document.pdf

# 指定输出目录和音色
python -m ai_content_automation run -i docs.md -o ./output -v zh-CN-YunxiNeural
```

### 3. 分步执行

```bash
# Step 1: 解析文档
python -m ai_content_automation parse -i document.pdf -o outline.json

# Step 2: 生成脚本
python -m ai_content_automation script -i outline.json -o script.md

# Step 3: 生成配音
python -m ai_content_automation tts -s script.md -o ./audio

# Step 4: 创建Remotion项目并渲染
python -m ai_content_automation render -p ./project -o video.mp4

# Step 5: 提交到GitHub（可选）
python -m ai_content_automation commit -m "生成新视频"
```

## 目录结构

```
ai-content-automation/
├── SKILL.md                    # 技能定义文件
├── README.md                   # 本文件
├── requirements.txt            # Python依赖
├── __main__.py                 # 主入口
├── scripts/                    # 核心脚本
│   ├── __init__.py            # CLI入口
│   ├── pipeline.py            # 完整流水线
│   ├── pdf_parser.py          # PDF解析
│   ├── script_generator.py    # 脚本生成
│   ├── tts_engine.py          # TTS配音
│   ├── remotion_render.py     # 视频渲染
│   └── github_mcp.py          # GitHub归档
├── pdf-parser/                # PDF解析模块
├── remotion/                  # Remotion模块
├── tts-engine/                # TTS配音模块
└── github-mcp/                # GitHub归档模块
```

## 环境要求

- Python 3.10+
- Node.js 18+
- ffmpeg（用于最终视频合成）

## 配置

### 环境变量（可选）

在 `.env` 文件中配置：

```bash
# TTS音色（默认：zh-CN-XiaoxiaoNeural）
EDGE_TTS_VOICE=zh-CN-XiaoxiaoNeural

# GitHub（可选）
GITHUB_TOKEN=ghp_xxxxx
```

## 输出产物

```
output/
├── outline.json          # 解析后的大纲
├── script.md              # 视频脚本
├── audio/                 # 配音文件
│   ├── segment_001.mp3
│   ├── segment_001.srt
│   └── timeline.json
├── remotion-project/     # Remotion项目
│   ├── src/Video.tsx
│   └── package.json
└── videos/
    └── final.mp4         # 最终视频
```

## 触发关键词

- PDF转视频
- 文档生成视频
- AI自动做视频
- 内容自动化生产
- 从PDF生成教学视频

## 许可证

MIT License
