import os
import re
from datetime import datetime

def normalize_spacing(name):
    # Replace multiple spaces with single space
    name = re.sub(r"\s+", " ", name)

    # Normalize spacing around hyphens: " - " format
    name = re.sub(r"\s*-\s*", " - ", name)

    # Remove space before file extension
    name = re.sub(r"\s+\.", ".", name)

    return name.strip()

def rename_files(root_dir, log_file):
    pattern = re.compile(r"\(([^)]+)\)")

    with open(log_file, "a", encoding="utf-8") as log:
        log.write(f"\n--- Run at {datetime.now()} ---\n")

        for dirpath, dirnames, filenames in os.walk(root_dir):
            for filename in filenames:
                old_path = os.path.join(dirpath, filename)

                # Replace (text) with - text
                new_filename = pattern.sub(r"- \1", filename)

                # Normalize spacing
                new_filename = normalize_spacing(new_filename)

                if new_filename != filename:
                    new_path = os.path.join(dirpath, new_filename)

                    if not os.path.exists(new_path):
                        os.rename(old_path, new_path)
                        msg = f"RENAMED: {old_path} -> {new_path}"
                    else:
                        msg = f"SKIPPED (exists): {new_path}"

                    print(msg)
                    log.write(msg + "\n")

if __name__ == "__main__":
    root_directory = input("Enter directory path: ").strip()
    log_file = os.path.join(root_directory, "rename_log.txt")

    rename_files(root_directory, log_file)

    print(f"\nDone. Log saved to: {log_file}")