# AI Content Automation - Main Entry
import argparse
import os
import sys


def main():
    parser = argparse.ArgumentParser(
        description="AI Content Automation - 从PDF/MD自动生成视频"
    )
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # run - 完整流程
    run_parser = subparsers.add_parser("run", help="一键执行完整流程")
    run_parser.add_argument("-i", "--input", required=True, help="输入文件(PDF/MD)")
    run_parser.add_argument("-o", "--output", default="./output", help="输出目录")
    run_parser.add_argument(
        "-v", "--voice", default="zh-CN-XiaoxiaoNeural", help="TTS音色"
    )

    # parse - 解析文档
    parse_parser = subparsers.add_parser("parse", help="解析PDF/MD文档")
    parse_parser.add_argument("-i", "--input", required=True, help="输入文件")
    parse_parser.add_argument("-o", "--output", default="outline.json", help="输出文件")

    # script - 生成脚本
    script_parser = subparsers.add_parser("script", help="生成视频脚本")
    script_parser.add_argument("-i", "--input", required=True, help="大纲文件")
    script_parser.add_argument("-o", "--output", default="script.md", help="输出脚本")

    # tts - 生成配音
    tts_parser = subparsers.add_parser("tts", help="生成TTS配音")
    tts_parser.add_argument("-s", "--script", required=True, help="脚本文件")
    tts_parser.add_argument("-o", "--output", default="./audio", help="输出目录")
    tts_parser.add_argument(
        "-v", "--voice", default="zh-CN-XiaoxiaoNeural", help="音色"
    )

    # render - 渲染视频
    render_parser = subparsers.add_parser("render", help="渲染视频")
    render_parser.add_argument(
        "-p", "--project", required=True, help="Remotion项目目录"
    )
    render_parser.add_argument("-o", "--output", default="video.mp4", help="输出视频")

    # commit - Git归档
    commit_parser = subparsers.add_parser("commit", help="提交到GitHub")
    commit_parser.add_argument("-m", "--message", required=True, help="提交信息")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # 创建输出目录
    output_dir = (
        getattr(args, "output", None) or getattr(args, "project", None) or "./output"
    )
    if output_dir and output_dir != "./output" or args.command == "run":
        os.makedirs(output_dir, exist_ok=True)

    # 执行对应命令
    if args.command == "run":
        from .pipeline import run_full_pipeline

        run_full_pipeline(args.input, args.output, args.voice)
    elif args.command == "parse":
        from .pdf_parser import parse_document

        parse_document(args.input, args.output)
    elif args.command == "script":
        from .script_generator import generate_script

        generate_script(args.input, args.output)
    elif args.command == "tts":
        from .tts_engine import generate_tts

        generate_tts(args.script, args.output, args.voice)
    elif args.command == "render":
        from .remotion_render import render_video

        render_video(args.project, args.output)
    elif args.command == "commit":
        from .github_mcp import commit_to_github

        commit_to_github(args.message)


if __name__ == "__main__":
    main()
