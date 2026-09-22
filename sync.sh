#!/usr/bin/env bash
set -euo pipefail

# NITYC-MCC-Tools 同期スクリプト
# fork したリポジトリに upstream（本家）のスキル更新を取り込む。
# - upstream remote が未登録なら自動で登録する
# - 未コミットの変更がある場合は中止する（作業中の成果物を守るため）

UPSTREAM_URL="https://github.com/atsuki-seo/NITYC-MCC-Tools.git"
UPSTREAM_BRANCH="main"

for arg in "$@"; do
  case "$arg" in
    --help|-h)
      cat <<'EOF'
使い方: ./sync.sh [オプション]

オプション:
  --help, -h  この使い方を表示

スクリプトの動作:
  1. 未コミットの変更がないか確認（あれば中止）
  2. upstream remote の登録確認（未登録なら自動登録）
  3. upstream から最新を取得してマージ
  4. 結果サマリを表示

自分の授業成果物（output/ 配下）はマージの影響を受けません。
コンフリクトが起きた場合は、表示される案内に従ってください。
EOF
      exit 0
      ;;
    *)
      echo "不明なオプション: $arg" >&2
      echo "使い方は ./sync.sh --help を参照" >&2
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

section() {
  echo ""
  echo "${C_BOLD}${C_CYAN}== $1 ==${C_RESET}"
}
ok()   { echo "${C_GREEN}[OK]${C_RESET}      $1"; }
warn() { echo "${C_YELLOW}[WARN]${C_RESET}    $1"; }
err()  { echo "${C_RED}[ERROR]${C_RESET}   $1" >&2; }

# git リポジトリ内か確認
if ! git rev-parse --git-dir >/dev/null 2>&1; then
  err "git リポジトリではありません"
  exit 1
fi

cd "$(git rev-parse --show-toplevel)"

# 1. 作業ツリーの確認
section "作業ツリーの確認"
if [ -n "$(git status --porcelain)" ]; then
  err "未コミットの変更があります"
  echo ""
  git status --short
  echo ""
  echo "${C_BOLD}先に変更をコミットするか退避してください:${C_RESET}"
  echo "  git add -A && git commit -m \"作業中の変更\"   # コミットする"
  echo "  git stash                                      # 一時退避する"
  exit 1
fi
ok "未コミットの変更なし"

CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"
if [ "$CURRENT_BRANCH" != "$UPSTREAM_BRANCH" ]; then
  warn "現在のブランチは '$CURRENT_BRANCH' です（通常は '$UPSTREAM_BRANCH' で実行します）"
fi

# 2. upstream remote の確認
section "upstream の確認"
if git remote get-url upstream >/dev/null 2>&1; then
  ok "upstream: $(git remote get-url upstream)"
else
  warn "upstream が未登録のため自動登録します"
  git remote add upstream "$UPSTREAM_URL"
  ok "upstream を登録: $UPSTREAM_URL"
fi

# 3. 取得とマージ
section "upstream から取得"
if ! git fetch upstream "$UPSTREAM_BRANCH"; then
  err "upstream の取得に失敗しました（ネットワーク接続を確認してください）"
  exit 1
fi
ok "取得完了"

BEFORE="$(git rev-parse HEAD)"
NEW_COMMITS="$(git rev-list --count "HEAD..upstream/$UPSTREAM_BRANCH")"

if [ "$NEW_COMMITS" -eq 0 ]; then
  section "サマリ"
  echo "${C_GREEN}${C_BOLD}✓ 既に最新です${C_RESET}"
  exit 0
fi

echo ""
echo "${C_BOLD}取り込む更新（$NEW_COMMITS 件）:${C_RESET}"
git log --oneline "HEAD..upstream/$UPSTREAM_BRANCH" | sed 's/^/  /'

section "マージ"
if git merge "upstream/$UPSTREAM_BRANCH" --no-edit; then
  ok "マージ完了"
else
  err "コンフリクトが発生しました"
  echo ""
  echo "${C_BOLD}対応方法:${C_RESET}"
  echo "  1. 以下のファイルを編集してコンフリクトを解消する"
  git diff --name-only --diff-filter=U | sed 's/^/     - /'
  echo "  2. git add <解消したファイル>"
  echo "  3. git commit"
  echo ""
  echo "  中止して元に戻す場合: ${C_BOLD}git merge --abort${C_RESET}"
  exit 1
fi

# 4. サマリ
section "サマリ"
echo "更新されたファイル:"
git diff --stat "$BEFORE" HEAD | sed 's/^/  /'
echo ""
echo "${C_GREEN}${C_BOLD}✓ 同期完了${C_RESET}"

if ! git diff --quiet "$BEFORE" HEAD -- '.claude/skills/*/requirements.txt'; then
  echo ""
  warn "依存パッケージが更新されています。./bootstrap.sh を実行してください"
fi
