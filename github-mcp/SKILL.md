---
name: ai-content-automation-github
description: GitHub归档模块。自动将生成的视频代码、脚本提交到GitHub仓库。
---

# GitHub归档模块

## 功能

- 自动初始化Git仓库（可选）
- 提交更改到GitHub
- 创建Release包
- 同步文档

## 使用方式

```bash
# 初始化仓库
python -m github_mcp init --repo owner/repo

# 提交所有更改
python -m github_mcp commit --message "生成新视频: 教程第一章"

# 创建版本标签
python -m github_mcp release --tag v1.0.0 --notes "发布视频v1.0.0"
```

## 配置

### 环境变量

```bash
# 二选一
GITHUB_TOKEN=ghp_xxxxxxxxxxxx
# 或使用 GitHub CLI（需要登录）
gh auth login
```

### 初始化

```bash
# 方式1: GitHub CLI
gh auth login

# 方式2: Token
export GITHUB_TOKEN=ghp_xxxxx
```

## 工作流程

1. 首次使用需配置GitHub访问
2. 每次生成视频后可选择是否归档
3. 自动创建包含视频代码和素材的提交

## 依赖

- git
- github-cli (gh)
- PyGithub
