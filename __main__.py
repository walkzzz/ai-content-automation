"""
AI Content Automation - 主入口点

使用方法:
    python -m ai_content_automation run -i document.pdf
    python -m ai_content_automation parse -i document.pdf -o outline.json
"""

import sys
import os

# 添加scripts目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "scripts"))

from scripts import main

if __name__ == "__main__":
    main()
