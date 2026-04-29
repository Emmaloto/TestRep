import os
import json
import argparse
from datetime import datetime
from PyPDF2 import PdfReader, PdfWriter

def get_pdf_title(reader):
    if reader.metadata and reader.metadata.title:
        return reader.metadata.title.strip()
    return None

def update_pdf_title(file_path, new_title):
    reader = PdfReader(file_path)
    writer = PdfWriter()

    # Copy pages
    for page in reader.pages:
        writer.add_page(page)

    # Copy existing metadata and update title
    metadata = reader.metadata or {}
    new_metadata = {}

    for key, value in metadata.items():
        if value:
            new_metadata[key] = str(value)

    new_metadata["/Title"] = new_title
    writer.add_metadata(new_metadata)

    with open(file_path, "wb") as f:
        writer.write(f)

def process_pdfs(root_dir, dry_run=False):
    changes = []

    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if not filename.lower().endswith(".pdf"):
                continue

            file_path = os.path.join(dirpath, filename)
            file_name_no_ext = os.path.splitext(filename)[0]

            try:
                reader = PdfReader(file_path)
                old_title = get_pdf_title(reader)

                if old_title and old_title != file_name_no_ext:
                    msg_type = "DRY-RUN" if dry_run else "UPDATED"

                    if not dry_run:
                        update_pdf_title(file_path, file_name_no_ext)

                    change_record = {
                        "file": file_path,
                        "old_title": old_title,
                        "new_title": file_name_no_ext,
                        "timestamp": datetime.now().isoformat(),
                        "mode": "dry-run" if dry_run else "applied"
                    }

                    changes.append(change_record)
                    print(f"{msg_type}: {file_path}")

            except Exception as e:
                print(f"ERROR: {file_path} -> {e}")

    return changes

def save_log(changes):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(os.getcwd(), f"pdf_title_changes_{timestamp}.json")

    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(changes, f, indent=2, ensure_ascii=False)

    print(f"\nLog saved to: {log_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update PDF Title metadata to match filename")
    parser.add_argument("directory", help="Root directory to scan")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without modifying files")

    args = parser.parse_args()

    changes = process_pdfs(args.directory, dry_run=args.dry_run)

    if changes:
        save_log(changes)
    else:
        print("No changes needed.")