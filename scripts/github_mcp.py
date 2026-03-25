"""
GitHub归档模块
"""

import os
import subprocess
import json


def commit_to_github(message, repo_path=".", files=None):
    """提交更改到GitHub"""

    if files is None:
        files = ["."]

    # 检查git是否可用
    if not is_git_available():
        print("⚠️ Git未安装或未配置")
        return False

    # 检查是否是git仓库
    if not is_git_repo(repo_path):
        print("⚠️ 当前目录不是Git仓库")
        print("💡 请先运行: git init")
        return False

    # 添加文件
    for f in files:
        subprocess.run(["git", "add", f], cwd=repo_path)

    # 提交
    result = subprocess.run(
        ["git", "commit", "-m", message], cwd=repo_path, capture_output=True, text=True
    )

    if result.returncode == 0:
        print(f"✅ 提交成功: {message}")

        # 检查是否关联远程仓库
        if has_remote(repo_path):
            # 推送到远程
            push_result = subprocess.run(
                ["git", "push"], cwd=repo_path, capture_output=True, text=True
            )
            if push_result.returncode == 0:
                print("✅ 已推送到远程仓库")
            else:
                print(f"⚠️ 推送失败: {push_result.stderr}")
        else:
            print("💡 未关联远程仓库，请手动 git push")
    else:
        print(f"⚠️ 提交失败: {result.stderr}")

    return result.returncode == 0


def create_release(tag, notes, repo_path="."):
    """创建GitHub Release"""

    # 尝试使用GitHub CLI
    result = subprocess.run(
        ["gh", "release", "create", tag, "--title", tag, "--notes", notes],
        cwd=repo_path,
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        print(f"✅ Release创建成功: {tag}")
    else:
        print(f"⚠️ Release创建失败: {result.stderr}")

    return result.returncode == 0


def init_repo(repo_url, output_dir="."):
    """初始化Git仓库并关联远程"""

    # 初始化
    subprocess.run(["git", "init"], cwd=output_dir)

    # 添加远程
    if repo_url:
        subprocess.run(["git", "remote", "add", "origin", repo_url], cwd=output_dir)

    print(f"✅ Git仓库初始化完成: {output_dir}")

    return True


def is_git_available():
    """检查git是否可用"""
    result = subprocess.run(["git", "--version"], capture_output=True)
    return result.returncode == 0


def is_git_repo(path):
    """检查是否是git仓库"""
    result = subprocess.run(
        ["git", "rev-parse", "--git-dir"], cwd=path, capture_output=True
    )
    return result.returncode == 0


def has_remote(path):
    """检查是否有远程仓库"""
    result = subprocess.run(
        ["git", "remote", "-v"], cwd=path, capture_output=True, text=True
    )
    return bool(result.stdout.strip())


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法:")
        print("  python -m github_mcp commit <提交信息>")
        print("  python -m github_mcp release <标签> <说明>")
        sys.exit(1)

    command = sys.argv[1]

    if command == "commit" and len(sys.argv) >= 3:
        commit_to_github(sys.argv[2])
    elif command == "release" and len(sys.argv) >= 4:
        create_release(sys.argv[2], sys.argv[3])
    else:
        print("参数错误")
