# NITYC-MCC-Tools

弓削商船高等専門学校（NITYC）の教育業務を支援するClaude Codeスキル集。高専モデルコアカリキュラム（MCC）に基づく情報系分野（V-D）の参照資料とスキルを提供する。

## 概要

- MCCに基づいたシラバス作成を支援
- 情報系分野（プログラミング、ソフトウェア、計算機工学、ネットワーク等）に対応
- テスト問題の自動生成とMoodle XMLでの出力を支援

## 含まれるファイル

| ファイル/フォルダ | 説明 |
|------------------|------|
| `docs/Kosen-MCC2023-Tech.pdf` | MCC2023原本 |
| `.claude/skills/class-syllabus/` | シラバス作成スキル |
| `.claude/skills/class-syllabus-parse/` | シラバス解析スキル（後続スキルの共通前処理） |
| `.claude/skills/class-test/` | テスト問題生成スキル |
| `specs/` | スキル間の共有契約（出力レイアウト・スキーマ・対話規約） |
| `CLAUDE.md` | Claude Code用の指示ファイル |

## セットアップ

`./bootstrap.sh` を実行すると依存チェックと Python パッケージ導入を行う。`--help` で使い方表示。

手動で入れるもの:

- [Python 3](https://www.python.org/) — ランタイム
  - [openpyxl](https://openpyxl.readthedocs.io/) — シラバス Excel 操作（bootstrap.sh が pip install --user）

## スキルの実行順序・ユースケース

正規フローは `syllabus → syllabus-parse → test`。

**どこから始めるか**:

- **新規科目を立ち上げる**: `class-syllabus` から入る（シラバス作成 → 以降の運用フローへ）
- **既存シラバスを流用する**: `class-test` から直接入る
  - 初回実行時に `class-syllabus-parse`（シラバス解析の共通前処理）が `class-test` から自動案内される

```mermaid
flowchart TD
    S[class-syllabus<br/>シラバス作成] --> P[class-syllabus-parse<br/>シラバス解析]
    P --> T[class-test<br/>テスト生成]
```

補足:

- `class-syllabus-parse` はセッション冒頭で明示実行しておく。重い生成スキルはセッションを分けて都度 parse からやり直す。

## 出典

- [高専機構 モデルコアカリキュラム（令和5年度版）](https://kosen-k.go.jp/wp/wp-content/uploads/2023/12/2c383e29-7e20-4b20-af19-ca3737450665.pdf)
