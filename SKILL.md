---
name: ai-content-automation
description: AI内容自动化生产工具 - 从PDF/MD文档自动生成完整视频。集成PDF解析、视频渲染（TTS配音+画面）能力。当用户提到PDF转视频、文档生成视频、AI自动做视频、内容自动化生产、从PDF生成教学视频时使用此技能。
compatibility: 需要 Python 3.10+, Node.js 18+, ffmpeg, git
---

# AI Content Automation - 内容自动化生产

> 从 PDF/MD 文档一键生成完整视频（配音+画面）

## 核心能力

| 模块 | 功能 | 状态 |
|------|------|------|
| **PDF解析** | 提取PDF/MD内容，生成结构化大纲 | ✅ 稳定 |
| **脚本生成** | 清理Markdown格式，生成自然语音脚本 | ✅ 优化 |
| **TTS配音** | 文本转语音，支持多种中文声音 | ✅ 优化 |
| **视频渲染** | FFmpeg直接生成（稳定）/ Remotion | ✅ 双方案 |

## 工作流

```
输入文档(PDF/MD)
    ↓
┌─────────────────────────────────────┐
│  Step 1: PDF解析            │
│  提取文本、生成结构化大纲    │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  Step 2: 脚本生成             │
│  清理Markdown，生成自然脚本      │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  Step 3: TTS配音               │
│  生成配音+字幕，自动合并音频      │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  Step 4: 视频渲染              │
│  FFmpeg生成视频（稳定方案）     │
└─────────────────────────────────────┘
    ↓
输出视频 (output/*.mp4)
```

## 安装

```bash
# 克隆项目
git clone https://github.com/walkzzz/ai-content-automation.git
cd ai-content-automation

# 安装Python依赖
pip install -r requirements.txt

# 安装Node.js依赖（首次创建项目时自动安装）
npm install
```

## 使用方式

### 一键执行完整流程

```bash
python -m ai_content_automation run -i document.pdf -o ./output
python -m ai_content_automation run -i 文档.md -o ./output -v zh-CN-YunxiNeural
```

### 分步执行

```bash
# Step 1: 解析文档
python -m ai_content_automation parse -i input.pdf -o outline.json

# Step 2: 生成脚本
python -m ai_content_automation script -i outline.json -o script.md

# Step 3: 生成配音
python -m ai_content_automation tts -s script.md -o ./audio -v zh-CN-XiaoxiaoNeural

# Step 4: 渲染视频
python -m ai_content_automation render -p ./project -o video.mp4 --audio ./audio
```

## 命令参数

| 命令 | 参数 | 说明 |
|------|------|------|
| `run` | `-i/--input`, `-o/--output`, `-v/--voice` | 一键执行 |
| `parse` | `-i/--input`, `-o/--output` | 解析文档 |
| `script` | `-i/--input`, `-o/--output` | 生成脚本 |
| `tts` | `-s/--script`, `-o/--output`, `-v/--voice`, `--list` | 生成配音 |
| `render` | `-p/--project`, `-o/--output`, `--audio` | 渲染视频 |

## TTS语音选择

```bash
# 列出所有可用语音
python -m ai_content_automation tts --list

# 使用不同语音
-v zh-CN-XiaoxiaoNeural  # 晓晓 - 通用女声（默认）
-v zh-CN-YunxiNeural     # 云希 - 通用男声
-v zh-CN-XiaoyiNeural   # 晓伊 - 活泼女声
-v zh-CN-YunyangNeural  # 云扬 - 专业男声
```

## 配置

### 环境变量（可选）

在 `.env` 文件中配置：

```bash
# TTS默认音色
EDGE_TTS_VOICE=zh-CN-XiaoxiaoNeural

# GitHub（可选）
GITHUB_TOKEN=ghp_xxxxx
```

## 输出产物

```
output/
├── outline.json          # 结构化大纲
├── script.md             # 视频脚本
├── audio/                # 配音文件
│   ├── segment_001.mp3   # 各片段
│   ├── segment_001.srt   # 字幕
│   ├── all_audio.mp3     # 合并后音频
│   └── timeline.json     # 时间轴
├── videos/               # 视频
│   └── final.mp4         # 最终视频
└── remotion-project/   # Remotion项目（可选）
```

## 触发关键词

- PDF转视频
- 文档生成视频
- AI自动做视频
- 内容自动化生产
- 从PDF生成教学视频
- 视频自动生成
- TTS配音
- 视频渲染

## 注意事项

1. **首次运行**需要安装依赖，建议在空闲网络环境下执行
2. **视频渲染**使用FFmpeg稳定方案，无需Remotion
3. **TTS配音**需要网络连接（edge-tts免费）
4. **GitHub归档**需要配置GitHub CLI或Token

## 版本

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.1.0 | 2026-03-25 | 优化TTS脚本质量，添加FFmpeg稳定渲染方案 |
| 1.0.0 | 2026-03-25 | 初始版本，4模块集成 |
