#!/usr/bin/env bash
# class-list.sh - outputディレクトリからシラバス一覧を取得して表示する
#
# 使い方:
#   ./class-list.sh              # テーブル形式で一覧表示
#   ./class-list.sh -p           # パスのみ出力（他スクリプトから利用向け）
#   ./class-list.sh -d DIR       # outputディレクトリを指定
#   ./class-list.sh -h           # ヘルプ表示

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OUTPUT_DIR="${SCRIPT_DIR}/output"
PATH_ONLY=false

usage() {
  cat <<'EOF'
Usage: class-list.sh [OPTIONS]

outputディレクトリ内のシラバスMarkdownファイルを検索し、一覧表示する。

Options:
  -d DIR   outputディレクトリを指定 (デフォルト: スクリプトと同階層のoutput/)
  -p       パスのみ出力 (1行1パス、他スクリプトからの利用向け)
  -h       このヘルプを表示
EOF
  exit 0
}

while getopts "d:ph" opt; do
  case "$opt" in
    d) OUTPUT_DIR="$OPTARG" ;;
    p) PATH_ONLY=true ;;
    h) usage ;;
    *) usage ;;
  esac
done

if [[ ! -d "$OUTPUT_DIR" ]]; then
  echo "エラー: outputディレクトリが見つかりません: $OUTPUT_DIR" >&2
  exit 1
fi

# シラバスMarkdownファイルを収集
mapfile -t md_files < <(find "$OUTPUT_DIR" -maxdepth 2 -name '*.md' ! -path '*/tests/*' | sort)

if [[ ${#md_files[@]} -eq 0 ]]; then
  echo "シラバスMarkdownファイルが見つかりませんでした。" >&2
  exit 1
fi

# パスのみモード
if [[ "$PATH_ONLY" == true ]]; then
  printf '%s\n' "${md_files[@]}"
  exit 0
fi

# シラバスMDから基本情報を抽出する関数
extract_field() {
  local file="$1" field="$2"
  grep -m1 "| ${field} |" "$file" | sed 's/.*| '"${field}"' | \(.*\) |/\1/' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//'
}

# ヘッダー出力
printf "%-4s  %-24s  %-8s  %-16s  %-6s  %-12s  %s\n" \
  "#" "科目名" "年度" "学科" "学年" "開講期" "パス"
printf "%-4s  %-24s  %-8s  %-16s  %-6s  %-12s  %s\n" \
  "----" "------------------------" "--------" "----------------" "------" "------------" "----"

idx=0
for file in "${md_files[@]}"; do
  idx=$((idx + 1))
  subject=$(extract_field "$file" "教科名")
  year=$(extract_field "$file" "開講年度" | sed 's/年度$//')
  dept=$(extract_field "$file" "開設学科")
  grade=$(extract_field "$file" "対象学年")
  term=$(extract_field "$file" "開講期")

  printf "%-4s  %-24s  %-8s  %-16s  %-6s  %-12s  %s\n" \
    "$idx" "$subject" "$year" "$dept" "$grade" "$term" "$file"
done

echo ""
echo "合計: ${#md_files[@]} 件のシラバス"
