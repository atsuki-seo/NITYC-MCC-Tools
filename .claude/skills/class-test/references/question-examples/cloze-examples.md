# 穴埋め Cloze 作問例

情報工学科の授業（アルゴリズム、データ構造等）を想定した穴埋めCloze問題の例。

---

## 例1: 基礎（概念の穴埋め）

### 問題文
以下の文章の空欄を埋めよ。

キュー (Queue) は {1:MULTICHOICE:=FIFO#正解~LIFO#LIFOはスタックの特徴です~FILO#FILOはスタックの別名です} 方式のデータ構造であり、データの追加操作を {1:SHORTANSWER:=エンキュー#正解~%50%enqueue#英語でも可} 、取り出し操作を {1:SHORTANSWER:=デキュー#正解~%50%dequeue#英語でも可} という。

### 正解
- 空欄1: FIFO
- 空欄2: エンキュー
- 空欄3: デキュー

### Moodle XML上の注意
- defaultgrade = 3（サブ問題3つ × 各1点）
- MULTICHOICE はドロップダウンで表示される
- SHORTANSWER は表記揺れ（日本語/英語）に部分点で対応

### 設計意図
- 難易度: 基礎
- データ構造の基本用語の正確な知識を確認
- 選択式と記述式を混合して多角的に問う

---

## 例2: 標準（コードの穴埋め）

### 問題文
以下はスタックを配列で実装するPythonコードの一部である。空欄を埋めてコードを完成させよ。

```
class Stack:
    def __init__(self):
        self.data = []

    def push(self, value):
        self.data.{1:SHORTANSWER_C:=append#正解~%50%push#pushはリストのメソッドではありません}(value)

    def pop(self):
        if self.is_empty():
            return None
        return self.data.{1:SHORTANSWER_C:=pop#正解}()

    def is_empty(self):
        return {1:SHORTANSWER_C:=len(self.data) == 0#正解~%50%self.data == []#動作しますが len() を使う方が一般的です}
```

### 正解
- 空欄1: append
- 空欄2: pop
- 空欄3: len(self.data) == 0

### Moodle XML上の注意
- SHORTANSWER_C（大文字小文字区別あり）を使用（プログラミング言語の構文のため）
- コードは `<pre><code>` タグで囲み、CDATAで保護する
- defaultgrade = 3

### 設計意図
- 難易度: 標準
- Pythonのリスト操作メソッドとスタックの実装の理解を確認
- AI耐性: コード全体の文脈を理解しないと正解できない

---

## 例3: 応用（複合概念の穴埋め）

### 問題文
以下は二分探索木 (BST) に関する記述である。空欄を埋めよ。

二分探索木では、任意のノードについて、左部分木のすべての値はそのノードの値より {1:MULTICHOICE:=小さい#正解~大きい#大小関係が逆です~等しい#等しい値は通常、左右いずれかに統一して配置します} 。
要素数 n の二分探索木における探索の平均計算量は {1:SHORTANSWER:=O(log n)#正解~%50%O(logn)#スペースなしでも可} であるが、木が偏って一直線になった場合の最悪計算量は {1:SHORTANSWER:=O(n)#正解} となる。
この最悪ケースを回避するために、{1:SHORTANSWER:=AVL木#正解~%50%平衡二分探索木#広義では正解~%50%赤黒木#これも正解の一つです} などの平衡木が用いられる。

### 正解
- 空欄1: 小さい
- 空欄2: O(log n)
- 空欄3: O(n)
- 空欄4: AVL木（赤黒木、平衡二分探索木も許容）

### Moodle XML上の注意
- defaultgrade = 4（4つのサブ問題）
- 空欄4は複数の正解バリエーションを設定し、部分点で対応

### 設計意図
- 難易度: 応用
- BST の性質・計算量・発展的なデータ構造を横断的に問う
- 選択式と記述式の混合で多角的に理解度を確認
