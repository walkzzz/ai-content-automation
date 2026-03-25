---
name: ai-content-automation-remotion
description: Remotion视频渲染模块。使用Remotion框架生成视频代码并渲染成片。
---

# Remotion视频渲染模块

## 功能

- 基于脚本生成 Remotion 项目
- 渲染视频（支持字幕、动画）
- 合成音频轨道

## 使用方式

```bash
# 创建Remotion项目
python -m remotion_module create --script script.md --output ./project

# 渲染视频
python -m remotion_module render --project ./project --output video.mp4

# 预览（启动预览服务器）
python -m remotion_module preview --project ./project
```

## 项目结构

```
project/
├── src/
│   ├── Video.tsx        # 主视频组件
│   ├── Slide.tsx        # 幻灯片组件
│   ├── Caption.tsx      # 字幕组件
│   └── assets/          # 静态资源
├── public/              # 公开资源
├── package.json
└── remotion.config.ts
```

## 渲染命令

```bash
cd project
npx remotion render src/Video.tsx out video.mp4
```

## 依赖

- Node.js 18+
- @remotion/cli
- @remotion/node
