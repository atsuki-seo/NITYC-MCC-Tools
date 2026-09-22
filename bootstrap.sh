#!/usr/bin/env bash
set -euo pipefail

# NITYC-MCC-Tools セットアップスクリプト
# - 依存コマンドの存在チェック（無ければ案内）
# - Python パッケージの導入（pip install --user）

for arg in "$@"; do
  case "$arg" in
    --help|-h)
      cat <<'EOF'
使い方: ./bootstrap.sh [オプション]

オプション:
  --help, -h  この使い方を表示

スクリプトの動作:
  1. 依存コマンドの存在チェック（無ければ案内のみ、自動インストールはしない）
  2. .claude/skills/*/requirements.txt を pip3 install --user
  3. 末尾にサマリを表示
EOF
      exit 0
      ;;
    *)
      echo "不明なオプション: $arg" >&2
      echo "使い方は ./bootstrap.sh --help を参照" >&2
      exit 2
      ;;
  esac
done

# 色付け（TTY のときのみ）
if [ -t 1 ] && command -v tput >/dev/null 2>&1 && [ "$(tput colors 2>/dev/null || echo 0)" -ge 8 ]; then
  C_RESET="$(tput sgr0)"
  C_BOLD="$(tput bold)"
  C_GREEN="$(tput setaf 2)"
  C_YELLOW="$(tput setaf 3)"
  C_RED="$(tput setaf 1)"
  C_CYAN="$(tput setaf 6)"
else
  C_RESET=""; C_BOLD=""; C_GREEN=""; C_YELLOW=""; C_RED=""; C_CYAN=""
fi

# OS 判定
case "$(uname -s)" in
  Linux*)  OS=linux ;;
  Darwin*) OS=mac ;;
  *) echo "${C_RED}サポート外の OS です（Linux/macOS のみ対応）${C_RESET}" >&2; exit 1 ;;
esac

# サマリ用配列
declare -a OK_LIST=()
declare -a MISSING_LIST=()
declare -a TODO_LIST=()

section() {
  echo ""
  echo "${C_BOLD}${C_CYAN}== $1 ==${C_RESET}"
}
ok()    { echo "${C_GREEN}[OK]${C_RESET}      $1"; OK_LIST+=("$1"); }
miss()  { echo "${C_YELLOW}[MISSING]${C_RESET} $1"; MISSING_LIST+=("$1"); }
warn()  { echo "${C_YELLOW}[WARN]${C_RESET}    $1"; }
err()   { echo "${C_RED}[ERROR]${C_RESET}   $1" >&2; }
todo()  { TODO_LIST+=("$1"); }

# 依存コマンドチェック
check_cmd() {
  local cmd="$1" desc="$2" install_linux="$3" install_mac="$4"
  if command -v "$cmd" >/dev/null 2>&1; then
    ok "$cmd ($desc)"
  else
    miss "$cmd ($desc)"
    if [ "$OS" = "linux" ]; then
      todo "$cmd: $install_linux"
    else
      todo "$cmd: $install_mac"
    fi
  fi
}

section "依存コマンドの確認"
check_cmd python3 "シラバス Excel 操作のランタイム" \
  "sudo apt install python3 python3-pip" \
  "brew install python3"

# Python パッケージ
section "Python パッケージの導入"
if command -v python3 >/dev/null 2>&1; then
  REQ_FILES=( $(find .claude/skills -name requirements.txt -type f 2>/dev/null || true) )
  if [ "${#REQ_FILES[@]}" -eq 0 ]; then
    warn "requirements.txt が見つかりません"
  else
    for req in "${REQ_FILES[@]}"; do
      echo "  → $req"
      if python3 -m pip install --user -r "$req" >/dev/null 2>&1; then
        ok "$req をインストール"
      else
        # PEP 668 等で失敗した場合はメッセージを出して継続
        if python3 -m pip install --user --break-system-packages -r "$req" >/dev/null 2>&1; then
          ok "$req をインストール（--break-system-packages）"
        else
          err "$req のインストールに失敗"
          todo "Python パッケージ: 手動で 'python3 -m pip install --user -r $req' を実行（PEP 668 環境では venv を検討）"
        fi
      fi
    done
  fi
else
  warn "python3 が無いため Python パッケージの導入をスキップ"
fi

# サマリ
section "サマリ"
echo "${C_GREEN}OK: ${#OK_LIST[@]} 件${C_RESET}"
if [ "${#MISSING_LIST[@]}" -gt 0 ]; then
  echo "${C_YELLOW}MISSING: ${#MISSING_LIST[@]} 件${C_RESET}"
  for m in "${MISSING_LIST[@]}"; do echo "  - $m"; done
fi
if [ "${#TODO_LIST[@]}" -gt 0 ]; then
  echo ""
  echo "${C_BOLD}手動で対応してください:${C_RESET}"
  for t in "${TODO_LIST[@]}"; do echo "  - $t"; done
  exit 1
fi

echo ""
echo "${C_GREEN}${C_BOLD}✓ セットアップ完了${C_RESET}"
