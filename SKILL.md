---
name: ai-content-automation
description: AI内容自动化生产工具 - 从PDF/MD文档自动生成完整视频。集成PDF解析、视频渲染（Remotion）、TTS配音、GitHub归档四大能力。当用户提到PDF转视频、文档生成视频、AI自动做视频、内容自动化生产、从PDF生成教学视频时使用此技能。
compatibility: 需要 Node.js 18+, Python 3.10+, ffmpeg, git
---

# AI Content Automation - 内容自动化生产

> 从 PDF/MD 文档一键生成完整视频（配音+画面）

## 核心能力

| 模块 | 功能 | 依赖 |
|------|------|------|
| **PDF解析** | 提取PDF/MD内容，生成结构化大纲 | Python, pdfplumber/pymupdf |
| **视频渲染** | 使用Remotion生成视频代码并渲染 | Node.js, @remotion/cli |
| **TTS配音** | 文本转语音，自动同步时间轴 | edge-tts 或 azure-tts |
| **GitHub归档** | 自动提交代码到GitHub仓库 | GitHub CLI, git |

## 工作流

```
输入文档(PDF/MD)
    ↓
┌─────────────────────────────────────┐
│  Step 1: PDF解析                    │
│  提取文本、生成结构化大纲            │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  Step 2: 脚本生成                   │
│  基于大纲生成视频脚本、分镜           │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  Step 3: TTS配音                    │
│  生成旁白音频，自动时间轴             │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  Step 4: 视频渲染                   │
│  Remotion合成视频+音频               │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  Step 5: GitHub归档                 │
│  自动提交到仓库（可选）              │
└─────────────────────────────────────┘
    ↓
输出视频 (output/*.mp4)
```

## 使用方式

### 快速开始

```bash
# 方式1: 一键执行完整流程
ai-content-automation run --input document.pdf

# 方式2: 分步执行
ai-content-automation parse --input document.pdf
ai-content-automation script --大纲文件
ai-content-automation tts --script 脚本文件
ai-content-automation render --project 项目目录
ai-content-automation commit --message "生成新视频"
```

### 命令详解

| 命令 | 功能 | 示例 |
|------|------|------|
| `run` | 完整流程 | `ai-content-automation run -i docs.pdf -o ./output` |
| `parse` | 解析文档 | `ai-content-automation parse -i input.md -o outline.json` |
| `script` | 生成脚本 | `ai-content-automation script -i outline.json` |
| `tts` | 生成配音 | `ai-content-automation tts -s script.md -o audio/` |
| `render` | 渲染视频 | `ai-content-automation render -p ./project -o video.mp4` |
| `commit` | Git归档 | `ai-content-automation commit -m "update video"` |

## 配置

### 环境变量

在 `.env` 文件中配置：

```bash
# TTS服务
EDGE_TTS_VOICE=zh-CN-XiaoxiaoNeural
# 或 Azure TTS
AZURE_SPEECH_KEY=your_key
AZURE_SPEECH_REGION=eastus

# GitHub（可选）
GITHUB_TOKEN=ghp_xxxxx
GITHUB_REPO=owner/repo
```

### 依赖安装

```bash
# Python 依赖
pip install -r requirements.txt

# Node.js 依赖
cd remotion-project
npm install
```

## 子模块详情

### PDF解析模块

详细使用见 `pdf-parser/README.md`

### 视频渲染模块

详细使用见 `remotion/README.md`

### TTS配音模块

详细使用见 `tts-engine/README.md`

### GitHub归档模块

详细使用见 `github-mcp/README.md`

## 输出产物

```
output/
├── outline.json          # 解析后的大纲
├── script.md             # 视频脚本
├── audio/                # 配音文件
│   ├── segment_001.mp3
│   ├── segment_002.mp3
│   └── ...
├── remotion-project/    # Remotion项目
│   ├── src/
│   │   └── Video.tsx
│   └── package.json
└── videos/               # 最终视频
    └── final.mp4
```

## 触发关键词

- PDF转视频
- 文档生成视频
- AI自动做视频
- 内容自动化生产
- 从PDF生成教学视频
- 视频自动生成
- TTS配音
- Remotion视频

## 注意事项

1. **首次运行**需要安装依赖，建议在空闲网络环境下执行
2. **视频渲染**是耗时操作，根据时长可能需要数分钟到数十分钟
3. **TTS配音**需要网络连接（edge-tts免费，azure-tts需要key）
4. **GitHub归档**需要配置GitHub CLI或Token

## 版本

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0.0 | 2026-03-25 | 初始版本，4模块集成 |
