# 参加ガイド

このリポジトリは、各教員が **fork して自分の授業ワークスペースとして使い**、スキルの改善を本家（upstream）に還元する運用を前提としている。

- **fork した自分のリポジトリ**: 自分の授業の成果物を置く作業場
- **upstream（本家）**: スキル・仕様の正本。改善はここに集約する

---

## 1. セットアップ

### 1.1 fork する

```bash
gh repo fork atsuki-seo/NITYC-MCC-Tools --clone
cd NITYC-MCC-Tools
```

GitHub の UI から fork した場合は、自分のリポジトリを clone する。

### 1.2 依存を導入する

```bash
./bootstrap.sh
```

Python と openpyxl（シラバス Excel 操作用）を確認・導入する。不足があれば手動対応の案内が出る。

### 1.3 動かす

Claude Code を起動し、スキルを実行する。実行順序とユースケースは [README](README.md) を参照。

---

## 2. upstream の更新を取り込む

本家でスキルが改善されたら、自分の fork に取り込む。

```bash
./sync.sh
```

初回実行時に upstream remote を自動登録する。未コミットの変更がある場合は中止するので、先にコミットするか `git stash` で退避すること。

手動で行う場合は以下と同等:

```bash
git remote add upstream https://github.com/atsuki-seo/NITYC-MCC-Tools.git  # 初回のみ
git fetch upstream main
git merge upstream/main
```

### コンフリクトが起きたら

`output/` 配下（自分の授業成果物）は upstream 側で触らないため、通常はコンフリクトしない。発生するとすれば `.claude/skills/` や `specs/` を自分で編集している場合である。

その編集が**自分専用のカスタマイズ**なら、upstream 側を採用して自分の変更を捨ててよい。**改善として還元したいもの**なら、§ 3 の手順で PR にしてから同期する。

---

## 3. 改善を還元する

### 3.1 PR は目的ごとに分ける

1つの PR には1つの目的だけを含める。レビューの精度が変わる。

| PR の種類 | 含めるもの | 含めないもの |
|-----------|-----------|-------------|
| **スキル改善** | `.claude/skills/`, `specs/`, `docs/` | `output/` 配下 |
| **授業資料の追加** | `output/[YYYY]_[教科名]/` | `.claude/`, `specs/` |

スキルを直したついでに自分のシラバスもコミットする、という混在を避ける。スキル改善のレビューに他人の授業資料の差分が混ざると、変更の意図が追えなくなる。

### 3.2 手順

```bash
git switch -c fix-syllabus-rubric   # 作業ブランチを作る
# 変更する
git add <変更したファイル>            # git add -A は避ける（意図しないファイルが入る）
git commit -m "class-syllabus: ルーブリックの評価段階を3→4に"
git push -u origin fix-syllabus-rubric
gh pr create
```

### 3.3 コミットメッセージ

`対象: 変更内容` の形式で、日本語で書く。

```
class-test: 計算問題の有効数字指定を追加
specs: materials/ の追跡範囲を定義
```

### 3.4 スキルを変更するときの原則

`.claude/rules/skill-guidelines.md` に設計原則がある。特に以下は PR 前に確認すること。

- 禁止リストではなく、原則で正解を示す（「〜するな」より「〜する」）
- 全ケースで通用するアプローチがあるなら、条件分岐を入れない

---

## 4. 公開してよいものの線引き

**このリポジトリは public である。** 一度 push した内容は、PR を閉じても、コミットを取り消しても、git の履歴から消えない。

### 4.1 置いてよいもの

| 対象 | 理由 |
|------|------|
| シラバス（`output/*/*.md`, `*.xlsx`） | 学校公式に公開される情報 |
| 授業資料（`output/*/materials/` 配下の許可拡張子） | 学生に配布する前提の資料 |
| スキル・仕様（`.claude/`, `specs/`） | このリポジトリの本体 |

### 4.2 置いてはいけないもの

- 学生の氏名・学籍番号・成績・提出物
- 未公開の試験問題、および解答

試験問題は `output/*/tests/` に出力され、`.gitignore` で丸ごと追跡対象外になる。

### 4.3 .gitignore は内容を検査しない

`materials/` 配下は拡張子で追跡可否を判定している（許可: `.html` `.css` `.js` `.pdf` `.svg` `.png` `.jpg` `.jpeg`）。

**許可拡張子のファイルは、中身が何であれコミット対象になる。** 学生名簿を含む HTML を置けばそのまま公開される。拡張子による制限は事故を減らす措置であって、保証ではない。

詳細は [specs/output-layout.md](specs/output-layout.md) § 1.4 を参照。

### 4.4 materials/ は Web にも配信される

`output/*/materials/` 配下は git に入るだけでなく、`main` への push をトリガーに GitHub Pages へ自動デプロイされ、URL を知っていれば誰でも閲覧できる状態になる（[.github/workflows/pages.yml](.github/workflows/pages.yml)）。

- 配信されるのは `materials/` 配下のみ。シラバス（`*.xlsx` / `*.md`）・`docs/`・`.claude/` はサイトに含まれない
- `tests/` は git 追跡対象外のため、そもそもデプロイ対象に入らない
- 年度 → 科目 → 資料をたどれる一覧ページが自動生成されるため、URL を知らなくても資料に到達できる。検索エンジンにも拾われうる

fork したリポジトリを private にした場合、Pages の公開可否は GitHub のプラン設定に従う。公開したくない場合はリポジトリ設定で Pages を無効化すること。

### 4.5 push する前に

```bash
git status          # 意図しないファイルが入っていないか
git diff --cached   # 中身に個人情報が混ざっていないか
```

`git add -A` は使わず、ファイルを指定して add する習慣をつけると事故が減る。

---

## 5. 困ったら

- スキルの使い方: [README](README.md)
- 出力先・ファイル名の規約: [specs/output-layout.md](specs/output-layout.md)
- スキル設計の原則: `.claude/rules/skill-guidelines.md`
- それ以外: Issue を立てる
