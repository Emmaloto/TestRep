#!/usr/bin/env python3

import os
import yaml
import argparse
import json
from datetime import datetime

def load_yaml(yaml_path):
    with open(yaml_path, 'r') as f:
        return yaml.safe_load(f)

def normalize_name(name):
    return os.path.splitext(name)[0].lower()

def get_extension(filename):
    return os.path.splitext(filename)[1]

def build_mapping(yaml_data):
    mapping = {}
    for entry in yaml_data.get("files", []):
        prev = entry.get("prev")
        current = entry.get("current")

        if not prev or not current:
            continue

        mapping[normalize_name(prev)] = current

    return mapping

def rename_files(base_dir, mapping, dry_run=False):
    operations = []

    for root, _, files in os.walk(base_dir):
        for file in files:
            file_base = normalize_name(file)

            if file_base in mapping:
                old_path = os.path.join(root, file)
                new_name_raw = mapping[file_base]

                new_base, new_ext = os.path.splitext(new_name_raw)

                if new_ext:
                    final_name = new_name_raw
                else:
                    final_name = new_name_raw + get_extension(file)

                new_path = os.path.join(root, final_name)

                if os.path.exists(new_path):
                    print(f"[SKIP] Target exists: {new_path}")
                    continue

                print(f"[RENAME] {old_path} → {new_path}")

                if not dry_run:
                    os.rename(old_path, new_path)
                    operations.append({
                        "old": old_path,
                        "new": new_path
                    })

    return operations

def save_log(operations, log_path=None):
    if not operations:
        print("[INFO] No operations to log")
        return

    if not log_path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = f"rename_log_{timestamp}.json"

    with open(log_path, "w") as f:
        json.dump(operations, f, indent=2)

    print(f"[INFO] Log saved to {log_path}")

def undo_operations(log_file, dry_run=False):
    with open(log_file, "r") as f:
        operations = json.load(f)

    # Reverse order to avoid conflicts
    for op in reversed(operations):
        old_path = op["old"]
        new_path = op["new"]

        if not os.path.exists(new_path):
            print(f"[SKIP] Missing file (cannot undo): {new_path}")
            continue

        if os.path.exists(old_path):
            print(f"[SKIP] Original already exists: {old_path}")
            continue

        print(f"[UNDO] {new_path} → {old_path}")

        if not dry_run:
            os.rename(new_path, old_path)

def main():
    parser = argparse.ArgumentParser(description="Rename files with rollback support")

    parser.add_argument("yaml_file", nargs="?", help="Path to YAML file")
    parser.add_argument("directory", nargs="?", help="Directory to search")

    parser.add_argument("--dry-run", action="store_true", help="Preview changes only")
    parser.add_argument("--log", help="Custom log file path")
    parser.add_argument("--undo", help="Undo using log file")

    args = parser.parse_args()

    # Undo mode
    if args.undo:
        undo_operations(args.undo, dry_run=args.dry_run)
        return

    # Normal mode
    if not args.yaml_file or not args.directory:
        print("Error: yaml_file and directory are required unless using --undo")
        return

    yaml_data = load_yaml(args.yaml_file)
    mapping = build_mapping(yaml_data)

    print(f"[INFO] Loaded {len(mapping)} mappings")

    operations = rename_files(args.directory, mapping, dry_run=args.dry_run)

    if not args.dry_run:
        save_log(operations, args.log)

if __name__ == "__main__":
    main()