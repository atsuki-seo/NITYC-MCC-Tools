# class-slides スキル設計書

弓削商船高専向け授業用 Marp スライド資料を、シラバス Markdown をもとに生成する Claude Code スキルの設計書。

## 概要

- スキル名: `class-slides`
- 目的: シラバス Markdown の授業計画・到達目標・ルーブリック・試験/レポートスケジュール等をもとに、授業1回分の Marp 形式スライドを生成する。シーズン全回分の一括生成にも対応する。
- 連携: `class-syllabus` で生成されたシラバス MD を入力とし、`class-syllabus-parse` にパースを委譲する。`class-test` / `class-report` が生成した成果物を参照して提出物スライドを詳細展開する。

## 入出力契約

### 入力

- **必須**: シラバス Markdown
  - パス: `output/[YYYY]_[教科名]/[教科名].md`
  - スキーマ: `specs/syllabus-markdown-schema.md` に準拠
  - 利用するセクション: 基本情報 / 到達目標 / ルーブリック / 概要 / 授業計画 / 試験・レポートスケジュール / MCC 対応 / 評価割合
- **任意参照**:
  - `output/[YYYY]_[教科名]/tests/[テスト名]/[テスト名]_確認用.md`
  - `output/[YYYY]_[教科名]/reports/[レポート名]/[レポート名]_課題.md`
  - `output/[YYYY]_[教科名]/reports/[レポート名]/[レポート名]_ルーブリック.md`
  - 該当回のスライドに「今回の提出物」スライドを詳細展開するために参照する。該当ファイル未発見時は「シラバス記載の概要のみで簡略版」を生成し警告を出す。

### 出力

- **ファイルパス**: `output/[YYYY]_[教科名]/slides/classNN.md`
  - `NN` は2桁ゼロ埋めの回番号（ソート順保証のため）
  - 1回=1ファイル。シーズン一括生成時も回ごとに分割する
- **フロントマッター（全ファイル共通・固定）**:
  ```yaml
  ---
  marp: true
  theme: yuge
  paginate: true
  header: '<学校名> <学科> <科目名> <年度>講義資料'
  footer: ''
  math: mathjax
  ---
  ```
  - `header` はシラバス基本情報から自動構築する
  - `theme: yuge` は固定。CSS 本体はリポジトリ外で管理されている前提
- **スライド構造（標準）**:
  - 表紙（科目名・第 N 回・回タイトル）
  - 目次
  - 内容スライド群（30分=10枚目安、60分=20枚目安。1スライド箇条書き7〜10行目安）
  - 今回の提出物スライド（該当回のみ、tests/reports から展開）
  - 今回のまとめ
- **スライド区切り**: `---` 単独行（Marp 規約）
- **レイアウト規約**: `references/yuge-theme-layout.md` に従う（`flex-layout` / `columns` div / `natural-height` / `summary-positive` / Tips 囲み / mermaid ブロック等）

## アーキテクチャ

### スキルファイル構成

```
.claude/skills/class-slides/
├── SKILL.md                              # 処理フロー本体
├── references/
│   ├── yuge-theme-layout.md              # yuge テーマ規約集
│   └── slide-structure-guide.md          # 各回の推奨スライド構造と情報量ルール
```

### 依存関係

- `class-syllabus-parse`: シラバス MD のパースを委譲（`class-report` Step 0 と同じ方針）
- `specs/syllabus-markdown-schema.md`: 入力契約の正本
- 参考プロジェクト `compiler-teaching-document-nityc`: レイアウト規約の抽出元

## 処理フロー

```
Step 0: シラバスMD読み込み
 └─ class-syllabus-parse に委譲
     授業計画テーブル、到達目標、ルーブリック、試験/レポートスケジュール、MCC、評価割合を取得

Step 1: 対象範囲の確認
 ├─ AskUserQuestion: 全回一括 / 特定回のみ
 └─ 特定回モードの場合、回番号を聞く（複数可、例「1,3,5」）
    ※ 特定回モードでもシラバス全回の情報は読み込む（前後参照の用語統一のため）

Step 2: 授業時間と情報量の確認
 ├─ シラバスに授業時間（30分/60分/90分）の記載があれば自動採用
 └─ なければ AskUserQuestion で確認
    情報量目安: 30分=10枚、60分=20枚、90分=30枚、1スライド箇条書き7〜10行

Step 3: 全回の骨子生成
 各回について以下を作成:
 - 回番号 / 回タイトル / 授業時間 / 枚数目安
 - キーコンセプト（3〜5個）
 - 含める要素: 表紙 / 目次 / 導入 / 概念解説（mermaid図含む）/ 比較表 / 例題 / 提出物 / まとめ
 - 到達目標参照（ルーブリック項目 ID）
 - MCC 対応（V-D-*）
 - 提出物該当回の場合: tests/reports の参照パス

Step 4: 骨子プレビューと修正
 ├─ 全回の骨子一覧を Markdown テーブルで提示
 ├─ ユーザーからの修正指示ループ（例「第3回にlex実習を足して」）
 └─ OK で骨子確定

Step 5: 回ごとの詳細化ループ
 対象回数分繰り返す:
 Step 5.1 N回目のスライド本体を生成
   - 骨子に従ってスライドごとの Markdown を書く
   - yuge-theme-layout.md の規約に従う
   - 提出物要素がある回は tests/reports MD から設問・期限・ルーブリック概要を展開
   - 情報量ルール遵守（枚数目安±2枚）
 Step 5.2 プレビュー提示（スライド一覧 + 代表スライド抜粋）
 Step 5.3 修正指示ループ（変更差分ハイライトで提示）
 Step 5.4 OK 後ファイル出力 output/[YYYY]_[教科]/slides/classNN.md
 Step 5.5 「次の回に進みますか？」→ 次ループ or 中断

Step 6: 完了報告
 └─ 生成ファイル一覧 / 各回の枚数 / 未処理回を表示
```

## エラーハンドリング

| 状況 | 対処 |
|---|---|
| シラバス MD が見つからない | Step 0 で `class-syllabus-parse` が失敗 → ユーザーにパスを確認 |
| 授業計画テーブルの行が空 | Step 3 で該当回を骨子から除外、警告表示 |
| シラバスに授業時間の記載なし | Step 2 で AskUserQuestion |
| 指定回番号がシラバスにない | Step 1 で「該当回なし」エラー、有効な回番号リストを提示 |
| 提出物該当回で tests/reports 未発見 | シラバス概要のみで簡略版を生成、警告表示 |
| 出力先 `slides/` が未作成 | 自動作成 |
| `classNN.md` が既存 | AskUserQuestion: 上書き / スキップ / 別名保存 |
| 骨子段階で枚数が目安±2枚を超える | Step 4 で削減を提案（強制はしない） |
| MCC / ルーブリックが空欄 | 警告のみ、処理継続（スライド反映はスキップ） |

### エッジケース

- **特定回のみモード**: 指定回のみ骨子生成。全回のシラバスは読み込む
- **シーズン途中からの再開**: 既存 `classNN.md` を検出し、未生成回のみ提案
- **修正ループ**: 回数上限なし（ユーザー判断）。プレビューは変更差分ハイライトで提示し context を圧迫しない

## 受け入れ基準

1. **既存シラバスで実走**: 既存教科（例: `output/2025_コンパイラ/`）で全回一括生成を実行
   - 全回分の `classNN.md` が生成される
   - Marp 構文エラーなし（`marp --watch` でプレビュー可能）
   - 回ごとの枚数が目安±2枚に収まる
2. **参考リポとの見た目比較**: 生成ファイル1つを参考リポ `compiler-part0.md` と目視比較し、レイアウト規約が一致
3. **提出物展開**: 既存 `reports/*/課題.md` がある回のスライドに期限・概要・ルーブリック要約が展開されている
4. **特定回のみモード**: 「3,7回目のみ」指定で該当2ファイルだけ生成、他回は影響なし
5. **到達目標/MCC連携**: 各回スライドに到達目標番号が明示され、シラバスMD記載と一致

## スコープ外（YAGNI）

- Marp コマンドによる PDF / PPTX エクスポート自動化（スキル外。ユーザーが別途実行）
- 写真・イラストの自動挿入（mermaid 図のみ生成、写真は教員が後挿入）
- 他テーマへの対応（`theme: yuge` 固定）
- Marp 以外の形式（reveal.js 等）サポート

## 開発順序

1. `.claude/skills/class-slides/references/yuge-theme-layout.md` 作成
   - 参考リポ `compiler-teaching-document-nityc` から規約を抽出して文書化
2. `.claude/skills/class-slides/references/slide-structure-guide.md` 作成
   - 標準スライド構造と情報量ルール
3. `.claude/skills/class-slides/SKILL.md` 作成（Step 0〜6）
4. 既存教科1科目で受け入れ基準の実走確認

## ドキュメント更新

- **README.md**: スキル一覧に `class-slides` を追加
- **CLAUDE.md**: 変更不要（既にスキル総論のみ）
