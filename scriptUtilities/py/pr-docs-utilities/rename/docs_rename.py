#!/usr/bin/env python3

import os
import yaml
import argparse

def load_yaml(yaml_path):
    with open(yaml_path, 'r') as f:
        return yaml.safe_load(f)

def normalize_name(name):
    """Return filename without extension, lowercase"""
    return os.path.splitext(name)[0].lower()

def get_extension(filename):
    return os.path.splitext(filename)[1]

def build_mapping(yaml_data):
    """
    Returns dict:
    normalized prev name -> current name (raw)
    """
    mapping = {}
    for entry in yaml_data.get("files", []):
        prev = entry.get("prev")
        current = entry.get("current")

        if not prev or not current:
            continue

        mapping[normalize_name(prev)] = current

    return mapping

def rename_files(base_dir, mapping):
    for root, _, files in os.walk(base_dir):
        for file in files:
            file_base = normalize_name(file)

            if file_base in mapping:
                old_path = os.path.join(root, file)
                new_name_raw = mapping[file_base]

                # Determine extension behavior
                new_base, new_ext = os.path.splitext(new_name_raw)

                if new_ext:
                    # YAML provided extension → use it
                    final_name = new_name_raw
                else:
                    # Preserve original extension
                    final_name = new_name_raw + get_extension(file)

                new_path = os.path.join(root, final_name)

                # Avoid overwriting existing files
                if os.path.exists(new_path):
                    print(f"[SKIP] Target exists: {new_path}")
                    continue

                print(f"[RENAME] {old_path} → {new_path}")
                os.rename(old_path, new_path)

def main():
    parser = argparse.ArgumentParser(description="Rename files based on YAML mapping")
    parser.add_argument("yaml_file", help="Path to YAML file")
    parser.add_argument("directory", help="Directory to search")

    args = parser.parse_args()

    yaml_data = load_yaml(args.yaml_file)
    mapping = build_mapping(yaml_data)

    print(f"[INFO] Loaded {len(mapping)} mappings")
    rename_files(args.directory, mapping)

if __name__ == "__main__":
    main()

# Sample script usage:
# python docs_rename.py files.yaml "C:\Users\EmmaL\Desktop\TempStorage\Camilla - Spousal Sponsorship FINAL"