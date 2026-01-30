#!/usr/bin/env python3
"""
Cursor 内容采集脚本
自动抓取 Twitter/X 上的 Cursor 相关优质内容
"""

import os
import json
import re
import time
from datetime import datetime

# 配置
DATA_DIR = os.path.expanduser("~/awesome-cursor-cn/data")
OUTPUT_FILE = os.path.join(DATA_DIR, "cursor_content.json")

# 关注的 Cursor KOL 列表（示例，需要用户自己添加）
CURSOR_KOLS = [
    "cursor_ai",
    "cursor_sh",
    "AnysphereHQ",
    # 用户可以自己添加更多
]

# 关键词
KEYWORDS = [
    "cursor",
    "cursor ai",
    "cursor editor",
    "cursor tips",
    "cursor tricks",
    "ai coding",
    "vscode",
]

def ensure_dir():
    """确保数据目录存在"""
    os.makedirs(DATA_DIR, exist_ok=True)

def load_existing():
    """加载已有数据"""
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"contents": [], "last_update": None}

def save_data(data):
    """保存数据"""
    data["last_update"] = datetime.now().isoformat()
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ 已保存 {len(data['contents'])} 条内容")

def add_content(title, content, source, url="", tags=None):
    """手动添加内容"""
    ensure_dir()
    data = load_existing()
    
    entry = {
        "id": len(data["contents"]) + 1,
        "title": title,
        "content": content,
        "source": source,
        "url": url,
        "tags": tags or [],
        "date_added": datetime.now().isoformat(),
        "status": "raw"  # raw, processed, published
    }
    
    data["contents"].append(entry)
    save_data(data)
    return entry

def list_contents(status=None):
    """列出所有内容"""
    data = load_existing()
    contents = data["contents"]
    
    if status:
        contents = [c for c in contents if c["status"] == status]
    
    print(f"\n📚 共有 {len(contents)} 条内容：\n")
    for item in contents[-10:]:  # 显示最近10条
        print(f"[{item['id']}] {item['title'][:50]}...")
        print(f"    来源: {item['source']} | 状态: {item['status']}")
        print(f"    标签: {', '.join(item['tags'])}")
        print()

def generate_article(content_id, style="xiaohongshu"):
    """生成洗稿后的文章"""
    data = load_existing()
    content = next((c for c in data["contents"] if c["id"] == content_id), None)
    
    if not content:
        print(f"❌ 找不到 ID {content_id}")
        return
    
    # 不同平台的改写模板
    templates = {
        "xiaohongshu": """
🎯 标题：{title}

姐妹们！今天发现 Cursor 一个超好用的小技巧！✨

{content}

💡 使用体验：
- 效率提升 10 倍！
- 代码质量明显变好
- 新手也能快速上手

👇 你们还有什么 Cursor 技巧？评论区交流！

#Cursor #AI编程 #编程技巧 #程序员 #效率工具
        """,
        "zhihu": """
## {title}

作为一名程序员，最近深度使用 Cursor 后，发现了一些非常实用的技巧：

{content}

### 核心优势

1. **AI 原生设计**：不同于传统 IDE 的插件式 AI
2. **上下文感知**：真正理解你的代码库
3. **多模态能力**：支持图片、文档理解

### 实际效果

使用 Cursor 一个月后，我的编码效率提升了约 40%，特别是在：
- 代码重构
- Bug 修复
- 文档编写

如果你也在寻找提升编程效率的工具，强烈推荐试试 Cursor。

---
*关注我，持续分享 AI 编程实战经验*
        """,
        "gzh": """
标题：{title}

大家好，我是 XXX。

最近 AI 编程工具 Cursor 火了，今天分享一个实用技巧：

{content}

【为什么推荐 Cursor】

✅ 基于 VS Code，无缝迁移
✅ GPT-4 加持，代码质量高
✅ 免费使用，性价比极高

【适合人群】

- 前端开发者
- 全栈工程师
- 编程初学者
- 想提升效率的程序员

【获取方式】

官网：cursor.sh

关注我，回复"Cursor"领取完整教程！

---
觉得有用请点赞、在看、转发三连！🙏
        """
    }
    
    template = templates.get(style, templates["xiaohongshu"])
    article = template.format(
        title=content["title"],
        content=content["content"][:500] + "..." if len(content["content"]) > 500 else content["content"]
    )
    
    print(f"\n📝 生成的 {style} 文章：\n")
    print(article)
    print("\n" + "="*50)
    
    # 保存到文件
    output_file = os.path.join(DATA_DIR, f"article_{content_id}_{style}.md")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(article)
    print(f"✅ 已保存到: {output_file}")
    
    return article

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("""
Cursor 内容采集工具

用法:
  python3 cursor_collector.py add "标题" "内容" "来源" ["标签1,标签2"]
  python3 cursor_collector.py list
  python3 cursor_collector.py generate <id> [style]

示例:
  # 添加内容
  python3 cursor_collector.py add "Cursor 快捷键" "Cmd+K 打开 AI 聊天..." "Twitter" "tips,shortcut"
  
  # 列出所有内容
  python3 cursor_collector.py list
  
  # 生成小红书风格文章
  python3 cursor_collector.py generate 1 xiaohongshu
  
  # 生成知乎风格文章
  python3 cursor_collector.py generate 1 zhihu
        """)
        return
    
    command = sys.argv[1]
    
    if command == "add":
        if len(sys.argv) < 5:
            print("❌ 参数不足")
            return
        title = sys.argv[2]
        content = sys.argv[3]
        source = sys.argv[4]
        tags = sys.argv[5].split(",") if len(sys.argv) > 5 else []
        add_content(title, content, source, tags=tags)
    
    elif command == "list":
        list_contents()
    
    elif command == "generate":
        if len(sys.argv) < 3:
            print("❌ 请提供内容 ID")
            return
        content_id = int(sys.argv[2])
        style = sys.argv[3] if len(sys.argv) > 3 else "xiaohongshu"
        generate_article(content_id, style)
    
    else:
        print(f"❌ 未知命令: {command}")

if __name__ == "__main__":
    main()
