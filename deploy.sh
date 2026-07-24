#!/usr/bin/env bash
# =============================================================================
#  Evennia 一键部署同步脚本
#  功能：备份 → 对比 → 同步 → 语法检查 → Django检查 → reload/restart → 回滚
#  用法：./deploy.sh [源目录] [目标目录]
# =============================================================================
set -euo pipefail

# ── 颜色 ──
RED='\033[1;31m'; GREEN='\033[1;32m'; YELLOW='\033[1;33m'
CYAN='\033[1;36m'; BLUE='\033[1;34m'; NC='\033[0m'; BOLD='\033[1m'
OK="${GREEN}✔${NC}"; FAIL="${RED}✘${NC}"

# ── 全局配置 ──
SRC_DIR="${1:-${PWD}}"
DST_DIR="${2:-${HOME}/mygame}"
BACKUP_DIR="${HOME}/backup"
SYNC_DIRS=("typeclasses" "commands" "world" "web")
EXCLUDE_LIST=(
    "__pycache__" "*.pyc" "*.pyo" ".git" ".idea" ".vscode"
    "Thumbs.db" ".DS_Store" "*.tmp" "*.sqlite3" "*.db3"
    "server" "logs" "media" "staticfiles" ".gitignore"
)
LOG_FILE="${DST_DIR}/sync.log"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="mygame_${TIMESTAMP}"
CHANGED_FILES=0
START_TIME=$(date +%s)
MAX_BACKUPS=10
EXCLUDE_ARGS=""

# ── 输出函数 ──
log()    { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG_FILE"; }
info()   { echo -e "  ${CYAN}$*${NC}"; log "$*"; }
ok()     { echo -e "  ${OK} ${GREEN}$*${NC}"; log "✔ $*"; }
fail()   { echo -e "  ${FAIL} ${RED}$*${NC}"; log "✘ $*"; }
step()   { echo -e "\n${BOLD}${BLUE}$*${NC}"; log "── $* ──"; }
warn()   { echo -e "  ${YELLOW}⚠ $*${NC}"; log "⚠ $*"; }

# ── 构建排除参数 ──
build_exclude_args() {
    EXCLUDE_ARGS=""
    for pattern in "${EXCLUDE_LIST[@]}"; do
        EXCLUDE_ARGS="$EXCLUDE_ARGS --exclude='$pattern'"
    done
}

# ── 重启 Evennia ──
restart_evennia() {
    cd "$DST_DIR" || return 1
    evennia stop &>/dev/null 2>&1 || true
    sleep 2
    if evennia start &>/dev/null 2>&1; then
        return 0
    fi
    return 1
}

# ── 恢复备份 ──
restore_backup() {
    local backup_path="$1"
    step "正在恢复备份..."

    if [[ ! -d "$backup_path" ]]; then
        fail "备份不存在: $backup_path"
        return 1
    fi

    cd "$DST_DIR" 2>/dev/null && evennia stop &>/dev/null 2>&1 || true
    sleep 2

    eval rsync -a --delete $EXCLUDE_ARGS "$backup_path/" "$DST_DIR/" 2>/dev/null
    ok "备份已恢复: $(basename "$backup_path")"

    if restart_evennia; then
        ok "Evennia 已恢复到上一版本并重新启动"
    else
        fail "恢复后启动仍然失败，请手动检查！"
    fi
}

# ── 致命错误 ──
error_exit() {
    fail "$1"
    if [[ -n "${2:-}" ]]; then
        restore_backup "$2"
    fi
    exit 1
}

# =============================================================================
# 主流程
# =============================================================================

echo ""
echo -e "${BOLD}${CYAN}╔══════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${CYAN}║   Evennia 一键部署同步脚本 v1.0              ║${NC}"
echo -e "${BOLD}${CYAN}╚══════════════════════════════════════════════╝${NC}"

log "========== 开始同步 =========="
build_exclude_args

# ── ① 检查源目录 ──
step "① 检查源目录"
if [[ ! -d "$SRC_DIR" ]]; then
    error_exit "源目录不存在: $SRC_DIR"
fi
if [[ ! -d "$SRC_DIR/commands" ]]; then
    error_exit "源目录缺少 commands/ 子目录，请确认路径正确"
fi
ok "源目录: $SRC_DIR"
ok "目标目录: $DST_DIR"

# ── ② 创建备份 ──
step "② 创建备份 ($BACKUP_NAME)"
mkdir -p "$BACKUP_DIR"
if [[ -d "$DST_DIR" ]]; then
    eval rsync -a --delete $EXCLUDE_ARGS "$DST_DIR/" "$BACKUP_DIR/$BACKUP_NAME/" 2>/dev/null
    ok "备份已创建: $BACKUP_DIR/$BACKUP_NAME"
else
    mkdir -p "$DST_DIR"
    warn "目标目录不存在，已创建: $DST_DIR"
fi

# ── ③ 比较文件 ──
step "③ 比较文件"
dry_run_output=$(eval rsync -avn --delete $EXCLUDE_ARGS "$SRC_DIR/" "$DST_DIR/" 2>/dev/null \
    | grep -v '^sending\|^sent\|^total\|^\.\/$' || true)

if [[ -z "$dry_run_output" ]]; then
    ok "没有任何变化，退出"
    echo ""
    exit 0
fi

CHANGED_FILES=$(echo "$dry_run_output" | grep -c '[^[:space:]]' || echo 0)
echo "$dry_run_output" | head -30
if [[ $CHANGED_FILES -gt 30 ]]; then
    echo "  ... 还有 $((CHANGED_FILES - 30)) 个文件发生变化"
fi
info "共 $CHANGED_FILES 个文件发生变化"

# ── ④ 同步 ──
step "④ 同步文件"
for dir in "${SYNC_DIRS[@]}"; do
    if [[ -d "$SRC_DIR/$dir" ]]; then
        eval rsync -a --delete $EXCLUDE_ARGS "$SRC_DIR/$dir/" "$DST_DIR/$dir/" 2>/dev/null
        ok "同步 $dir"
    else
        warn "跳过 $dir（目录不存在）"
    fi
done

# 同步根目录文件（非目录）
eval rsync -a --delete $EXCLUDE_ARGS --exclude='*/' "$SRC_DIR/" "$DST_DIR/" 2>/dev/null
ok "同步根目录文件"

# ── ⑤ collectstatic ──
step "⑤ 检查静态资源"
if echo "$dry_run_output" | grep -qE "web/static/|web/templates/" 2>/dev/null; then
    info "检测到静态资源变更，执行 collectstatic..."
    cd "$DST_DIR" || true
    if evennia collectstatic --noinput &>/dev/null 2>&1; then
        ok "collectstatic 完成"
    else
        warn "collectstatic 失败（可忽略，非致命错误）"
    fi
else
    ok "无需 collectstatic"
fi

# ── ⑥ 清除缓存 ──
step "⑥ 清除缓存"
find "$DST_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$DST_DIR" -name "*.pyc" -delete 2>/dev/null || true
find "$DST_DIR" -name "*.pyo" -delete 2>/dev/null || true
ok "缓存已清除"

# ── ⑦ Python 语法检查 ──
step "⑦ Python 语法检查"
compile_errors=0
for dir in "${SYNC_DIRS[@]}"; do
    if [[ -d "$DST_DIR/$dir" ]]; then
        if ! python3 -m compileall -q "$DST_DIR/$dir" 2>/dev/null; then
            compile_errors=1
            break
        fi
    fi
done

if [[ $compile_errors -eq 1 ]]; then
    error_exit "Python 语法错误" "$BACKUP_DIR/$BACKUP_NAME"
fi
ok "Python 语法检查通过"

# ── ⑧ Django 检查 ──
step "⑧ Django 检查"
cd "$DST_DIR" || true
if command -v evennia &>/dev/null; then
    if evennia check &>/dev/null 2>&1; then
        ok "Django 检查通过"
    else
        warn "Django 检查有警告（非致命）"
    fi
else
    warn "evennia 命令不可用，跳过 Django 检查"
fi

# ── ⑨ 重载服务 ──
step "⑨ 重载服务"

cd "$DST_DIR" || true
if evennia reload &>/dev/null 2>&1; then
    ok "Reload 成功"
else
    warn "Reload 失败，尝试 Restart..."
    if restart_evennia; then
        ok "Restart 成功"
    else
        error_exit "服务启动失败，已回滚" "$BACKUP_DIR/$BACKUP_NAME"
    fi
fi

# ── ⑩ 清理旧备份 ──
step "⑩ 清理旧备份"
backup_count=$(ls -1d "$BACKUP_DIR"/mygame_* 2>/dev/null | wc -l)
if [[ $backup_count -gt $MAX_BACKUPS ]]; then
    to_delete=$((backup_count - MAX_BACKUPS))
    ls -1dt "$BACKUP_DIR"/mygame_* 2>/dev/null | tail -n "$to_delete" | while read -r old; do
        rm -rf "$old"
        info "已删除旧备份: $(basename "$old")"
    done
    ok "已清理 $to_delete 个旧备份（保留最近 $MAX_BACKUPS 份）"
else
    ok "备份数量 $backup_count/$MAX_BACKUPS，无需清理"
fi

# ── 统计 ──
END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))

echo ""
echo -e "${BOLD}${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}${GREEN}  同步完成${NC}"
echo -e "${BOLD}${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "  变化文件: ${YELLOW}${CHANGED_FILES}${NC}"
echo -e "  同步目录: ${CYAN}${SYNC_DIRS[*]}${NC}"
echo -e "  备份位置: ${CYAN}${BACKUP_DIR}/${BACKUP_NAME}${NC}"
echo -e "  耗时:     ${YELLOW}${ELAPSED}秒${NC}"
echo -e "  日志:     ${CYAN}${LOG_FILE}${NC}"
echo -e "${BOLD}${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

log "========== 同步完成 (耗时${ELAPSED}秒) =========="
exit 0