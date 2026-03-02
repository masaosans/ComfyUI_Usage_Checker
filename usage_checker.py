import os
import json
import re
import folder_paths
from nodes import NODE_CLASS_MAPPINGS


class UsageCheckerNode:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "workflow_dir": ("STRING", {"default": "user/default/workflows"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "run"
    CATEGORY = "utils"

    # =====================================================
    # メイン処理
    # =====================================================

    def run(self, workflow_dir):

        workflow_dir = os.path.abspath(workflow_dir)

        used_node_types = set()
        used_model_files = set()
        dependency_graph = {}

        # ① 全モデルを先に取得（Ultra v4の核）
        all_models = self.scan_all_model_files()
        model_basename_map = {k.lower(): k for k in all_models.keys()}

        # ② workflowスキャン
        for root, _, files in os.walk(workflow_dir):
            for file in files:
                if not file.endswith(".json"):
                    continue
                if file.startswith("."):
                    continue

                self.scan_workflow(
                    os.path.join(root, file),
                    used_node_types,
                    used_model_files,
                    dependency_graph,
                    model_basename_map
                )

        # ③ custom_nodes解析（既存機能保持）
        custom_nodes_dir = folder_paths.get_folder_paths("custom_nodes")[0]
        top_level_dirs = self.get_top_level_custom_nodes(custom_nodes_dir)

        node_type_to_path = self.build_node_type_path_map(custom_nodes_dir)

        removable_dirs = self.detect_removable_directories(
            top_level_dirs,
            node_type_to_path,
            used_node_types
        )

        unused_models = set(all_models.keys()) - used_model_files

        # ④ レポート生成
        report = []
        report.append("===== USAGE REPORT =====\n")

        report.append("---- Used Custom Nodes ----")
        for nt in sorted(used_node_types):
            path = node_type_to_path.get(nt, "")
            report.append(f"{nt} ({path})")

        report.append("\n---- Removable Custom Node Directories ----")
        for d in sorted(removable_dirs):
            report.append(f"{os.path.basename(d)} ({d})")

        report.append("\n---- Used Models ----")
        for m in sorted(used_model_files):
            report.append(f"{m} ({all_models.get(m, '')})")

        report.append("\n---- Unused Models ----")
        for m in sorted(unused_models):
            report.append(f"{m} ({all_models.get(m, '')})")

        report.append("\n---- Dependency Summary ----")
        report.append(f"Used Nodes: {len(used_node_types)}")
        report.append(f"Used Models: {len(used_model_files)}")
        report.append(f"Removable Directories: {len(removable_dirs)}")

        return ("\n".join(report),)

    # =====================================================
    # Workflow解析（Ultra v4）
    # =====================================================

    def scan_workflow(self, path, used_node_types, used_model_files,
                      dependency_graph, model_basename_map):

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return

        # ノードタイプ回収（既存機能維持）
        nodes = []
        if isinstance(data, dict):
            if isinstance(data.get("nodes"), dict):
                nodes = data["nodes"].values()
            elif isinstance(data.get("nodes"), list):
                nodes = data["nodes"]
        elif isinstance(data, list):
            nodes = data

        for node in nodes:
            node_type = node.get("type")
            if node_type:
                used_node_types.add(node_type)
                dependency_graph.setdefault(node_type, [])

        # 🔥 JSON全域文字列スキャン
        all_strings = self.extract_all_strings(data)

        for text in all_strings:

            # ---- LoRAタグ検出 ----
            for lora in self.extract_lora_tags(text):
                if lora.lower() in model_basename_map:
                    real_name = model_basename_map[lora.lower()]
                    used_model_files.add(real_name)

            # ---- Embedding検出 ----
            for emb in self.extract_embeddings(text):
                if emb.lower() in model_basename_map:
                    real_name = model_basename_map[emb.lower()]
                    used_model_files.add(real_name)

            # ---- basename直接一致 ----
            base = os.path.basename(text).lower()
            if base in model_basename_map:
                real_name = model_basename_map[base]
                used_model_files.add(real_name)

    # =====================================================
    # JSON再帰文字列抽出
    # =====================================================

    def extract_all_strings(self, obj):

        results = []

        if isinstance(obj, dict):
            for v in obj.values():
                results.extend(self.extract_all_strings(v))

        elif isinstance(obj, list):
            for item in obj:
                results.extend(self.extract_all_strings(item))

        elif isinstance(obj, str):
            results.append(obj)

        return results

    # =====================================================
    # LoRAタグ抽出
    # =====================================================

    def extract_lora_tags(self, text):

        results = set()

        matches = re.findall(r"<lora:([\w\-\_\.]+)", text)
        for m in matches:
            if not m.endswith(".safetensors"):
                m += ".safetensors"
            results.add(m)

        return results

    # =====================================================
    # Embedding抽出
    # =====================================================

    def extract_embeddings(self, text):

        results = set()

        matches = re.findall(r"embedding:([\w\-\_\.]+)", text)
        matches += re.findall(r"<embedding:([\w\-\_\.]+)>", text)

        for m in matches:
            if not m.endswith(".pt"):
                m += ".pt"
            results.add(m)

        return results

    # =====================================================
    # 全モデル取得
    # =====================================================

    def scan_all_model_files(self):

        all_models = {}

        for category, entry in folder_paths.folder_names_and_paths.items():

            paths = entry[0] if isinstance(entry, tuple) else entry

            if not isinstance(paths, list):
                continue

            for base_path in paths:

                if not os.path.exists(base_path):
                    continue

                for root, _, files in os.walk(base_path):
                    for file in files:
                        if self.is_model_filename(file):
                            full_path = os.path.join(root, file)
                            all_models[file] = full_path

        return all_models

    # =====================================================
    # custom_nodes解析（既存維持）
    # =====================================================

    def get_top_level_custom_nodes(self, custom_nodes_dir):
        return {
            os.path.join(custom_nodes_dir, d)
            for d in os.listdir(custom_nodes_dir)
            if os.path.isdir(os.path.join(custom_nodes_dir, d))
        }

    def build_node_type_path_map(self, custom_nodes_dir):

        mapping = {}

        for node_type, cls in NODE_CLASS_MAPPINGS.items():
            try:
                module = __import__(cls.__module__, fromlist=[""])
                file_path = module.__file__
            except Exception:
                continue

            if file_path and custom_nodes_dir in file_path:
                base_dir = file_path.split(custom_nodes_dir)[-1]
                base_dir = base_dir.strip("\\/").split(os.sep)[0]
                mapping[node_type] = os.path.join(custom_nodes_dir, base_dir)

        return mapping

    def detect_removable_directories(self, top_level_dirs, node_type_to_path, used_node_types):

        dir_to_node_types = {}

        for node_type, path in node_type_to_path.items():
            dir_to_node_types.setdefault(path, set()).add(node_type)

        removable = set()

        for d in top_level_dirs:

            node_types = dir_to_node_types.get(d, set())

            if not node_types:
                removable.add(d)
                continue

            if all(nt not in used_node_types for nt in node_types):
                removable.add(d)

        return removable

    # =====================================================
    # モデル拡張子判定
    # =====================================================

    def is_model_filename(self, name):

        return isinstance(name, str) and name.lower().endswith((
            ".safetensors",
            ".ckpt",
            ".pt",
            ".pth",
            ".bin",
            ".onnx",
            ".gguf"
        ))
