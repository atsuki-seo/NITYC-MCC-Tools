# HTMLテンプレート

`class-material` の Step 4（HTML生成）で参照する。骨格と各コンポーネントのマークアップ。

---

## 1. 全体骨格

```html
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>[テーマ] | [教科名]</title>
<link rel="icon" href="assets/kousho.svg">
<link rel="stylesheet" href="assets/material.css">
</head>
<body>
<div class="wrap">

<header class="doc-head">
  <p class="eyebrow"><img class="crest" src="assets/kousho.svg" alt="" aria-hidden="true">[学校名] [学科名] [学年] [開講期]<br>
  [教科名]</p>
  <h1>[テーマ]</h1>
  <p class="doc-meta">担当: [担当教員] ／ [開講年度]年度</p>
</header>

<details class="toc" open>
  <summary>目次</summary>
  <ol>
    <li><a href="#s1">[節タイトル1]</a></li>
    <li><a href="#s2">[節タイトル2]</a></li>
  </ol>
</details>

<!-- ============ 1. [節タイトル1] ============ -->
<section id="s1">
  <h2><span class="num">1</span>[節タイトル1]</h2>
  ...
</section>

<footer class="doc-foot">
  <p>[教科名]／[テーマ]<br>
  <img class="crest" src="assets/kousho.svg" alt="" aria-hidden="true">[学校名] [学科名] [学年] [開講期] ― 担当: [担当教員]</p>
</footer>

</div>
</body>
</html>
```

### 1.1 アセット参照

校章とCSSは `assets/` 配下の共有ファイルを参照する。**SVGのパスデータやCSSをHTML内に埋め込まない。**

| 参照 | パス |
|------|------|
| スタイルシート | `assets/material.css` |
| 校章（favicon・本文中） | `assets/kousho.svg` |

校章は装飾であり情報を持たないため、`alt=""` + `aria-hidden="true"` とする。学校名は隣接するテキストが担う。

### 1.2 節の id と番号

- `section` の `id` は `s1`, `s2`, ... と連番にする（1始まり）
- `h2 .num` の数字と `id` の数字を一致させる
- 目次の `href` は全て対応する `section` の `id` を指す

生成後、目次のリンク数と `section` 数が一致することを確認する。

---

## 2. コンポーネント

### 2.1 本文

```html
<p>
  本文は常体で記述する。
  <span class="term">用語</span><span class="en">(term)</span> は初出時に原語を併記する。
  特に重要な命題は <strong>strong で囲む</strong>。
</p>

<ul>
  <li><span class="term">データ型</span><span class="en">(data type)</span> — 値の範囲と操作を定める規約</li>
</ul>
```

### 2.2 小見出し

節内をさらに分ける場合に `h3` を用いる。

```html
<h3>[小見出し]</h3>
```

### 2.3 注記ボックス

```html
<div class="note">
  <span class="label">本講の到達点</span>
  <ul>
    <li>[到達点1]</li>
    <li>[到達点2]</li>
  </ul>
</div>

<div class="note caution">
  <span class="label">誤りやすい点</span>
  <p>[注意内容]</p>
</div>
```

### 2.4 表

`.table-scroll` で必ず囲む。囲まないとスマートフォンで横にはみ出す。

```html
<div class="table-scroll">
<table>
  <thead>
    <tr><th>分類</th><th>保持する値</th><th>代表的な操作</th></tr>
  </thead>
  <tbody>
    <tr>
      <td>整数型</td>
      <td>小数部を持たない数</td>
      <td>四則演算、剰余、大小比較</td>
    </tr>
  </tbody>
</table>
</div>
```

数値列には `<td class="num-cell">` を用いる（中央揃え・等幅数字）。

### 2.5 擬似コード

```html
<pre><code>1. a ← 3
2. b ← 8
3. a ← b</code></pre>
```

`<pre>` 内は改行・空白がそのまま表示されるため、インデントを付けない。

### 2.6 図版

```html
<figure>
  <svg viewBox="0 0 580 150" role="img" aria-label="[図の内容説明]">
    ...
    <defs>
      <marker id="ah1" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto">
        <path d="M 0 0 L 9 4.5 L 0 9 z" fill="var(--c-accent)"/>
      </marker>
    </defs>
  </svg>
  <figcaption>
    図 [節番号]-[連番]　[説明文]
  </figcaption>
</figure>
```

詳細は `figure-guide.md` を参照する。

### 2.7 確認問題

```html
<div class="quiz">
  <span class="quiz-label">確認問題 [節番号]-[連番]</span>
  <p class="q-body">[設問文]</p>
  <ol class="choices">
    <li>[選択肢1]</li>
    <li>[選択肢2]</li>
    <li>[選択肢3]</li>
    <li>[選択肢4]</li>
  </ol>
  <details class="answer">
    <summary><span>解答</span></summary>
    <div class="answer-body">
      <p class="verdict">正解: (B)</p>
      <p>[正解の根拠]</p>
      <p>[各誤答がなぜ誤りか]</p>
    </div>
  </details>
</div>
```

- 選択肢の `(A)` 等は CSS が自動採番する。手で書かない
- `details` に `open` を付けない
- `summary` の中身は `<span>解答</span>` 固定（表示ラベルは CSS の `::before` が制御）

詳細は `quiz-guide.md` を参照する。

---

## 3. 節のコメント区切り

節の前にコメントを置き、編集時の見通しを確保する。

```html
<!-- ============ 1. データの持ち方が効率を決める ============ -->
```

---

## 4. 生成後チェック

- [ ] `<link>` のパスが `assets/material.css` になっているか
- [ ] 校章の参照が `assets/kousho.svg` になっているか（パスデータの埋め込みがないか）
- [ ] 目次のリンク数と `section` 数が一致するか
- [ ] `href="#sN"` と `id="sN"` が全て対応するか
- [ ] `h2 .num` の番号が `id` の連番と一致するか
- [ ] 全ての表が `.table-scroll` で囲まれているか
- [ ] 全ての `.quiz` に `details.answer` があるか
- [ ] SVG の `marker id` がページ内で重複していないか
- [ ] SVG内に色値の直書きがないか
- [ ] 予告・次回言及がないか
- [ ] 敬体が混入していないか
