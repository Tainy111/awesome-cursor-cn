#!/bin/bash
# Cursor 内容自动化工作流
# 每天自动执行：采集 → 洗稿 → 分发

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_DIR="$HOME/awesome-cursor-cn/data"
LOG_FILE="$DATA_DIR/automation.log"

# 确保目录存在
mkdir -p "$DATA_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 1. 采集内容（示例，实际需要从 API 或 RSS 获取）
collect_content() {
    log "开始采集内容..."
    
    # 这里可以集成 Twitter API、RSS 订阅等
    # 目前使用示例数据
    
    log "内容采集完成"
}

# 2. 生成多平台文章
generate_articles() {
    log "生成多平台文章..."
    
    cd "$SCRIPT_DIR/.."
    
    # 为最新的 3 条内容生成文章
    for id in 1 2 3; do
        for platform in xiaohongshu zhihu gzh; do
            if [ -f "$DATA_DIR/article_${id}_${platform}.md" ]; then
                log "文章 ${id} ${platform} 已存在，跳过"
            else
                log "生成文章 ${id} ${platform}..."
                python3 scripts/cursor_collector.py generate "$id" "$platform" 2>/dev/null || true
            fi
        done
    done
    
    log "文章生成完成"
}

# 3. 推送到 GitHub（更新 awesome 仓库）
push_to_github() {
    log "推送到 GitHub..."
    
    cd "$HOME/awesome-cursor-cn"
    
    git add -A
    git commit -m "Update: $(date '+%Y-%m-%d')" 2>/dev/null || true
    git push origin main 2>/dev/null || log "推送失败，请检查网络"
    
    log "GitHub 更新完成"
}

# 4. 发送通知
send_notification() {
    log "发送通知..."
    
    # 可以集成 Discord、钉钉等
    # 示例：发送到 Discord
    if [ -n "$DISCORD_WEBHOOK" ]; then
        curl -s -X POST "$DISCORD_WEBHOOK" \
            -H "Content-Type: application/json" \
            -d "{\"content\":\"🚀 Cursor 内容已更新！查看：https://github.com/Tainy111/awesome-cursor-cn\"}" \
            2>/dev/null || true
    fi
    
    log "通知发送完成"
}

# 主流程
main() {
    log "========== 开始自动化工作流 =========="
    
    collect_content
    generate_articles
    push_to_github
    send_notification
    
    log "========== 工作流完成 =========="
}

# 根据参数执行
if [ "$1" == "collect" ]; then
    collect_content
elif [ "$1" == "generate" ]; then
    generate_articles
elif [ "$1" == "push" ]; then
    push_to_github
elif [ "$1" == "notify" ]; then
    send_notification
else
    main
fi
