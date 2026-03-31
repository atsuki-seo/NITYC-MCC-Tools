# Moodle XML フォーマット仕様

Moodle 4.x の問題バンクにインポートするためのXML形式の完全仕様。

## 基本構造

```xml
<?xml version="1.0" encoding="UTF-8"?>
<quiz>
  <!-- カテゴリ設定（任意） -->
  <!-- 問題を列挙 -->
</quiz>
```

**重要な注意点**:
- `<?xml ...?>` 宣言はファイルの **1行目** に必ず記述する（先頭に空行やBOMを入れない）
- エンコーディングは **UTF-8** 必須
- ルート要素は `<quiz>` で、内部に複数の `<question>` を配置する

## カテゴリ設定

カテゴリは「ダミー問題」として挿入する。以降の問題はそのカテゴリに所属する。

```xml
<question type="category">
  <category>
    <text>$course$/アルゴリズム/小テスト1</text>
  </category>
  <info format="moodle_auto_format">
    <text></text>
  </info>
</question>
```

- `$course$/` はコースのトップカテゴリ
- `/` で区切ると階層構造になる
- カテゴリが存在しなければ自動作成される

## 共通タグ

すべての問題タイプで使用する共通タグ:

```xml
<question type="（問題タイプ）">
  <name>
    <text>Q01_問題名</text>
  </name>
  <questiontext format="html">
    <text><![CDATA[問題文（HTML可）]]></text>
  </questiontext>
  <generalfeedback format="html">
    <text><![CDATA[解答後に全員に表示されるフィードバック]]></text>
  </generalfeedback>
  <defaultgrade>1</defaultgrade>
  <penalty>0.3333333</penalty>
  <hidden>0</hidden>
  <idnumber>1</idnumber>
</question>
```

| タグ | 説明 |
|------|------|
| `<name><text>` | 問題名（管理用）。**ゼロパディング必須**（後述の命名規則を参照） |
| `<idnumber>` | 問題の数値ID。通し番号を設定し、Moodle内でのソート順を保証する |
| `<questiontext format="html">` | 問題文。format は `html` を標準とする |
| `<generalfeedback>` | 正誤問わず解答後に表示されるフィードバック |
| `<defaultgrade>` | デフォルト配点 |
| `<penalty>` | 複数回解答時のペナルティ率（0〜1） |
| `<hidden>` | 0 = 表示, 1 = 非表示 |

## テキスト内のHTML・数式

### HTMLの使用
問題文にHTMLを含む場合は **必ず CDATA** で囲む:
```xml
<text><![CDATA[<p>以下のコードの出力を答えよ。</p><pre><code>int x = 5;</code></pre>]]></text>
```

### LaTeX数式
MathJaxフィルタでレンダリングされる。デリミタは以下を使用:
- インライン: `\(ax^2 + bx + c = 0\)`
- ディスプレイ: `\[x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}\]`

`$$..$$` や `$...$` は非推奨（通貨記号と衝突するため）。

### 画像の埋め込み
```xml
<questiontext format="html">
  <text><![CDATA[<p>以下の図を見て答えよ。</p><p><img src="@@PLUGINFILE@@/diagram.png" alt="図"></p>]]></text>
  <file name="diagram.png" path="/" encoding="base64">（base64データ）</file>
</questiontext>
```

---

## 問題タイプ別テンプレート

### 1. 多肢選択 (multichoice)

#### 単一選択

```xml
<question type="multichoice">
  <name><text>Q01_多肢選択</text></name>
  <questiontext format="html">
    <text><![CDATA[<p>問題文をここに記述する。</p>]]></text>
  </questiontext>
  <generalfeedback format="html">
    <text><![CDATA[全体フィードバック。]]></text>
  </generalfeedback>
  <defaultgrade>2</defaultgrade>
  <penalty>0.3333333</penalty>
  <hidden>0</hidden>
  <single>true</single>
  <shuffleanswers>1</shuffleanswers>
  <answernumbering>abc</answernumbering>
  <correctfeedback format="html">
    <text>正解です。</text>
  </correctfeedback>
  <partiallycorrectfeedback format="html">
    <text>部分的に正解です。</text>
  </partiallycorrectfeedback>
  <incorrectfeedback format="html">
    <text>不正解です。</text>
  </incorrectfeedback>
  <answer fraction="100" format="html">
    <text>正解の選択肢</text>
    <feedback format="html">
      <text>この選択肢が正解である理由。</text>
    </feedback>
  </answer>
  <answer fraction="0" format="html">
    <text>誤答の選択肢A</text>
    <feedback format="html">
      <text>この選択肢が不正解である理由。</text>
    </feedback>
  </answer>
  <answer fraction="0" format="html">
    <text>誤答の選択肢B</text>
    <feedback format="html">
      <text>この選択肢が不正解である理由。</text>
    </feedback>
  </answer>
  <answer fraction="0" format="html">
    <text>誤答の選択肢C</text>
    <feedback format="html">
      <text>この選択肢が不正解である理由。</text>
    </feedback>
  </answer>
</question>
```

#### 複数選択

`<single>false</single>` に変更し、正解の fraction を分配する。不正解には **負の fraction** を設定する。

```xml
<single>false</single>
<answer fraction="50" format="html">
  <text>正解A</text>
  <feedback format="html"><text>正解です。</text></feedback>
</answer>
<answer fraction="50" format="html">
  <text>正解B</text>
  <feedback format="html"><text>正解です。</text></feedback>
</answer>
<answer fraction="-50" format="html">
  <text>不正解C</text>
  <feedback format="html"><text>不正解です。</text></feedback>
</answer>
```

| 属性/タグ | 説明 |
|-----------|------|
| `<single>` | `true` = 単一選択, `false` = 複数選択 |
| `<shuffleanswers>` | `1` = シャッフル, `0` = 固定順 |
| `<answernumbering>` | `abc`, `ABCD`, `123`, `none` |
| `fraction` | 正解=100, 不正解=0。複数選択時は合計100に分配 |

---

### 2. 数値問題 (numerical)

```xml
<question type="numerical">
  <name><text>Q02_数値</text></name>
  <questiontext format="html">
    <text><![CDATA[<p>問題文をここに記述する。整数で答えよ。</p>]]></text>
  </questiontext>
  <generalfeedback format="html">
    <text><![CDATA[全体フィードバック。]]></text>
  </generalfeedback>
  <defaultgrade>3</defaultgrade>
  <penalty>0.3333333</penalty>
  <hidden>0</hidden>
  <answer fraction="100" format="plain_text">
    <text>42</text>
    <tolerance>0</tolerance>
    <feedback format="html">
      <text>正解です。</text>
    </feedback>
  </answer>
  <answer fraction="0" format="plain_text">
    <text>*</text>
    <tolerance>0</tolerance>
    <feedback format="html">
      <text>不正解です。正解は42です。</text>
    </feedback>
  </answer>
</question>
```

| タグ | 説明 |
|------|------|
| `<tolerance>` | 許容誤差（0で完全一致） |
| `<tolerancetype>` | `1`=相対, `2`=絶対(nominal), `3`=幾何 |

---

### 3. 穴埋め Cloze (cloze)

```xml
<question type="cloze">
  <name><text>Q03_穴埋め</text></name>
  <questiontext format="html">
    <text><![CDATA[
<p>以下のコードの空欄を埋めよ。</p>
<pre><code>
def binary_search(arr, target):
    low = 0
    high = {1:SHORTANSWER_C:=len(arr) - 1#正解~%50%len(arr)-1#スペースの有無は許容}
    while low <= high:
        mid = (low + high) // {1:NUMERICAL:=2#正解}
        if arr[mid] == target:
            return mid
</code></pre>
    ]]></text>
  </questiontext>
  <generalfeedback format="html">
    <text><![CDATA[全体フィードバック。]]></text>
  </generalfeedback>
  <defaultgrade>2</defaultgrade>
  <penalty>0.3333333</penalty>
  <hidden>0</hidden>
</question>
```

**Cloze構文**:
```
{配点:タイプ:=正解#FB~%部分点%別解#FB~誤答#FB}
```

| タイプ | 略記 | 説明 |
|--------|------|------|
| `MULTICHOICE` | `MC` | ドロップダウン |
| `MULTICHOICE_V` | `MCV` | 縦並びラジオ |
| `SHORTANSWER` | `SA` | 記述（大文字小文字区別なし） |
| `SHORTANSWER_C` | `SAC` | 記述（大文字小文字区別あり） |
| `NUMERICAL` | `NM` | 数値 |

**注意**: question type は `"cloze"` を使用する。`<defaultgrade>` はサブ問題の配点合計と一致させる。

---

### 4. マッチング (matching)

```xml
<question type="matching">
  <name><text>Q04_マッチング</text></name>
  <questiontext format="html">
    <text><![CDATA[<p>各アルゴリズムと平均計算量を正しく対応させよ。</p>]]></text>
  </questiontext>
  <generalfeedback format="html">
    <text><![CDATA[全体フィードバック。]]></text>
  </generalfeedback>
  <defaultgrade>4</defaultgrade>
  <penalty>0.3333333</penalty>
  <hidden>0</hidden>
  <shuffleanswers>1</shuffleanswers>
  <correctfeedback format="html">
    <text>全問正解です。</text>
  </correctfeedback>
  <partiallycorrectfeedback format="html">
    <text>一部不正解があります。</text>
  </partiallycorrectfeedback>
  <incorrectfeedback format="html">
    <text>不正解です。</text>
  </incorrectfeedback>
  <subquestion format="html">
    <text>バブルソート</text>
    <answer><text>O(n^2)</text></answer>
  </subquestion>
  <subquestion format="html">
    <text>クイックソート</text>
    <answer><text>O(n log n)</text></answer>
  </subquestion>
  <subquestion format="html">
    <text>線形探索</text>
    <answer><text>O(n)</text></answer>
  </subquestion>
  <subquestion format="html">
    <text>二分探索</text>
    <answer><text>O(log n)</text></answer>
  </subquestion>
  <!-- ダミー選択肢 -->
  <subquestion format="html">
    <text></text>
    <answer><text>O(1)</text></answer>
  </subquestion>
</question>
```

- 最低3つの `<subquestion>` が必要
- ダミーは `<text>` を空にした `<subquestion>` で追加
- 個別ペアへのフィードバックはサポートされない

---

### 5. 記述問題 Short answer (shortanswer)

```xml
<question type="shortanswer">
  <name><text>Q05_記述</text></name>
  <questiontext format="html">
    <text><![CDATA[<p>後入れ先出し（LIFO）のデータ構造の名称を答えよ。</p>]]></text>
  </questiontext>
  <generalfeedback format="html">
    <text><![CDATA[正解はスタック (Stack) です。]]></text>
  </generalfeedback>
  <defaultgrade>3</defaultgrade>
  <penalty>0.3333333</penalty>
  <hidden>0</hidden>
  <usecase>0</usecase>
  <answer fraction="100" format="plain_text">
    <text>スタック</text>
    <feedback format="html">
      <text>正解です。</text>
    </feedback>
  </answer>
  <answer fraction="100" format="plain_text">
    <text>stack</text>
    <feedback format="html">
      <text>正解です。</text>
    </feedback>
  </answer>
  <answer fraction="100" format="plain_text">
    <text>Stack</text>
    <feedback format="html">
      <text>正解です。</text>
    </feedback>
  </answer>
  <answer fraction="0" format="plain_text">
    <text>*</text>
    <feedback format="html">
      <text>不正解です。正解はスタック (Stack) です。</text>
    </feedback>
  </answer>
</question>
```

| タグ | 説明 |
|------|------|
| `<usecase>` | `0` = 大文字小文字区別なし, `1` = 区別する |
| `*` | ワイルドカード（catch-all用） |

---

### 6. 計算問題 Calculated (calculated)

```xml
<question type="calculated">
  <name><text>Q06_計算</text></name>
  <questiontext format="html">
    <text><![CDATA[<p>要素数 {n} の配列に対してバブルソートを実行する場合、最悪計算量での比較回数を答えよ。</p>]]></text>
  </questiontext>
  <generalfeedback format="html">
    <text><![CDATA[バブルソートの最悪比較回数は n(n-1)/2 です。]]></text>
  </generalfeedback>
  <defaultgrade>5</defaultgrade>
  <penalty>0.3333333</penalty>
  <hidden>0</hidden>
  <shuffleanswers>0</shuffleanswers>
  <answer fraction="100">
    <text>{n}*({n}-1)/2</text>
    <tolerance>0.01</tolerance>
    <tolerancetype>1</tolerancetype>
    <correctanswerformat>1</correctanswerformat>
    <correctanswerlength>0</correctanswerlength>
    <feedback format="html">
      <text>正解です。</text>
    </feedback>
  </answer>
  <dataset_definitions>
    <dataset_definition>
      <status><text>private</text></status>
      <name><text>n</text></name>
      <type>calculatedsimple</type>
      <distribution><text>uniform</text></distribution>
      <minimum><text>5</text></minimum>
      <maximum><text>20</text></maximum>
      <decimals><text>0</text></decimals>
      <itemcount>10</itemcount>
      <dataset_items>
        <dataset_item><number>1</number><value>5</value></dataset_item>
        <dataset_item><number>2</number><value>8</value></dataset_item>
        <dataset_item><number>3</number><value>10</value></dataset_item>
        <dataset_item><number>4</number><value>12</value></dataset_item>
        <dataset_item><number>5</number><value>7</value></dataset_item>
        <dataset_item><number>6</number><value>15</value></dataset_item>
        <dataset_item><number>7</number><value>18</value></dataset_item>
        <dataset_item><number>8</number><value>6</value></dataset_item>
        <dataset_item><number>9</number><value>14</value></dataset_item>
        <dataset_item><number>10</number><value>20</value></dataset_item>
      </dataset_items>
      <number_of_items>10</number_of_items>
    </dataset_definition>
  </dataset_definitions>
</question>
```

| タグ | 説明 |
|------|------|
| `{n}` | 問題文・計算式中の変数 |
| `<answer><text>` | 計算式（Moodle関数使用可） |
| `<tolerance>` | 許容誤差 |
| `<dataset_definitions>` | 変数データセットの定義 |
| `<status>` | `private`=この問題専用 |
| `<distribution>` | `uniform`=一様分布 |
| `<minimum>`, `<maximum>` | 変数の範囲 |
| `<decimals>` | 小数点以下の桁数 |
| `<itemcount>`, `<number_of_items>` | データセット数（一致させる） |

**使用可能な数式関数**: `pow()`, `log()`, `sqrt()`, `abs()`, `ceil()`, `floor()`, `round()`, `sin()`, `cos()`, `exp()`, `pi()` 等（PHPの数学関数に準拠）

---

## 問題の命名規則とソート順

問題がMoodleの問題バンク上で正しい順序（1, 2, 3, ... 10, 11）で表示されるよう、以下のルールを適用する:

1. **`<name>` のゼロパディング**: 問題名は `Q01_`, `Q02_`, ... `Q26_` のように2桁でゼロパディングする。問題数が100以上の場合は3桁にする
2. **`<idnumber>` の設定**: 各問題に通し番号の `<idnumber>` を設定する（1, 2, 3, ...）。Moodle内部でのソート順を保証する
3. **カテゴリ内の一意性**: `<idnumber>` はカテゴリ内で一意であること

命名例:
```xml
<name><text>Q01_多肢選択_データ構造</text></name>
<idnumber>1</idnumber>
```

## 全体的な注意点

1. **CDATA**: HTMLやLaTeX、特殊文字を含む `<text>` は `<![CDATA[...]]>` で囲む
2. **BOMなし**: UTF-8 BOMがあるとインポートが失敗する場合がある
3. **fraction合計**: multichoiceの複数選択で正解のfraction合計は必ず100にする
4. **Cloze構文**: CDATA内に記述して、XMLパーサーへの干渉を防ぐ
5. **matchingの最低数**: 最低3ペア必要
6. **calculatedのデータセット**: 最低1セットは明示的に含める（10セット推奨）
7. **tolerance省略**: 省略すると0（完全一致のみ）になるので注意
