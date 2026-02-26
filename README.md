# ComfyUI_usage_checker

ComfyUI の全 workflow を横断して、未使用の model / custom_nodes を検出するツールです。

---

##  機能

- workflows フォルダを再帰的にスキャン
- models ディレクトリ配下を再帰的にスキャン
- custom_nodes ディレクトリ配下を再帰的にスキャン
- 使用されている model / node を集約
- 未使用の model / custom_nodes をレポート表示

---

## インストール方法

1. このフォルダを以下に配置:

ComfyUI/custom_nodes/ComfyUI_usage_checker/

2. ComfyUI を再起動

---

## 使い方

1. ノード追加
2. utils → ComfyUI Global Usage Checker
3. workflows ディレクトリを指定

---

## 判定ロジックについて

### Model
拡張子ベースで検出:

- .safetensors
- .ckpt
- .pt
- .bin
- .pth
- .onnx
- .gguf

### Custom Nodes
- custom_nodes 配下のフォルダ単位で判定
- .py を含むディレクトリをノードとして扱う

---

## ** 注意 ** 

- ノードタイプ名とフォルダ名が一致しない場合は誤検出の可能性があります
- モデルが UI 表示名とファイル名で違う場合も誤差が出る可能性があります


MIT
