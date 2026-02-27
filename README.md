# ComfyUI Usage Checker

ComfyUIの workflow を横断スキャンし、  
**未使用の models / custom_nodes を高精度で検出するツール**です。

---

# 🔥 特徴（Resolverベース完全版）

本ツールは推測ベースではありません。

ComfyUI内部の `folder_paths.get_full_path()` を利用し、  
**実際に解決可能なモデルのみを Used と判定する Resolver方式**を採用しています。

- 推測なし
- basename一致なし
- サブフォルダ完全対応
- Windows完全対応
- Embedding完全対応

---

# 主な機能

## 1. Workflow一括スキャン（再帰対応）

指定ディレクトリ配下の全 `.json` workflow を再帰的に解析。

対応形式：

- dict形式
- list形式
- ComfyUI旧形式
- ComfyUI新形式

---

## 2. Resolver方式モデル検出（最高精度）

workflow内のすべての文字列値に対して、以下を実行します。

```python
folder_paths.get_full_path(category, value)
```

全カテゴリに対して解決を試み、  
実際に解決できたもののみを Used Models と判定します。

対応カテゴリ例：

- checkpoints
- loras
- vae
- controlnet
- clip
- embeddings
- unet
- その他拡張カテゴリ

将来追加されるカテゴリにも自動対応します。

---

## 3. Embedding完全対応

以下形式を自動検出します。

```
embedding:xxx
<embedding:xxx>
```

`.pt`拡張子は自動補完されます。

---

## 4. Custom Nodes 使用状況解析

- workflowに登場した node_type を集計
- `NODE_CLASS_MAPPINGS` から実ファイルパスを特定
- 使用・未使用を判定

---

## 5. 削除可能 Custom Node ディレクトリ検出

custom_nodes直下ディレクトリ単位で：

- 一度も使われていない node_type のみを含むフォルダ
- nodeを一切持たないフォルダ

を「削除可能候補」として表示します。

出力例：

```
---- Removable Custom Node Directories ----
OldExtension (C:\ComfyUI\custom_nodes\OldExtension)
```

※ 自動削除は行いません（安全設計）

---

## 6. モデル未使用検出

modelsディレクトリ配下を再帰スキャンし、

- Used Models
- Unused Models

を明確に表示します。

---

# 出力例

```
===== USAGE REPORT =====

---- Used Custom Nodes ----
MyCustomNode (C:\ComfyUI\custom_nodes\MyCustomNode)

---- Removable Custom Node Directories ----
OldExtension (C:\ComfyUI\custom_nodes\OldExtension)

---- Used Models ----
dreamshaper.safetensors (C:\ComfyUI\models\checkpoints\dreamshaper.safetensors)

---- Unused Models ----
unused_model.safetensors (C:\ComfyUI\models\checkpoints\unused_model.safetensors)

---- Dependency Summary ----
Used Nodes: 42
Used Models: 18
Removable Directories: 3
```

---

# インストール

```
git clone https://github.com/masaosans/ComfyUI_usage_checker.git
```

`custom_nodes` フォルダに配置し、ComfyUIを再起動してください。

---

# 使い方

1. ノード追加 → `check usage model and node`
2. `workflow_dir` に workflow フォルダを指定

Windows環境では相対パス指定を推奨します。

例：

```
user/default/workflows
```

---

# 技術仕様

## モデル検出方式

従来の：

- INPUT_TYPES推測
- node_type推測
- キーワードヒューリスティック

は使用していません。

代わりに、

Resolver方式（ComfyUI内部解決エンジン利用）

のみで判定しています。

これにより：

- 同名モデル問題回避
- サブフォルダ完全対応
- 将来ノード追加への自動適応

を実現しています。

---

# 注意事項

- 削除は自己責任で行ってください
- 実行中のworkflowは解析対象外
- workflow内に保存されていない一時ロードモデルは検出できません
- 外部スクリプトからロードされるモデルは検出対象外です

---

# このツールの思想

拡張子検索ではなく、

**ComfyUI内部の実解決ロジックを利用する**

ことで、

将来耐性・高精度・安定性を兼ね備えた  
本格的 Usage Checker を実現します。

---

# ライセンス

MIT License
