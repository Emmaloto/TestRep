import csv
import sys
import os


# python budget_classifier.py transactions.csv 2

MAPPING_FILENAME = "BudgetCostAssociation.csv"


def load_mapping(mapping_file):
    """
    Loads Category,Keyword pairs into a list of tuples.
    Matching is done case-insensitively.
    """
    mappings = []

    with open(mapping_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            category = row["Category"].strip()
            keyword = row["Keyword"].strip().lower()
            mappings.append((category, keyword))

    return mappings


def classify_row(description, mappings):
    """
    Returns the first matching category based on keyword match.
    """
    description_lower = description.lower()

    for category, keyword in mappings:
        if keyword in description_lower:
            return category

    return ""


def process_transactions(input_path, name_column_number, mappings):
    output_path = generate_output_path(input_path)

    with open(input_path, newline="", encoding="utf-8") as infile, \
         open(output_path, "w", newline="", encoding="utf-8") as outfile:

        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        header = next(reader)
        header.append("Category")
        writer.writerow(header)

        name_index = name_column_number - 1

        for row in reader:
            if name_index >= len(row):
                row.append("")
                writer.writerow(row)
                continue

            description = row[name_index]
            category = classify_row(description, mappings)
            row.append(category)
            writer.writerow(row)

    print(f"\nOutput written to: {output_path}")


def generate_output_path(input_path):
    base, ext = os.path.splitext(input_path)
    return f"{base}_classified{ext}"


def main():
    if len(sys.argv) != 3:
        print("Usage: python budget_classifier.py <transactions_csv_path> <name_column_number>")
        sys.exit(1)

    transactions_path = sys.argv[1]
    name_column_number = int(sys.argv[2])

    if not os.path.exists(MAPPING_FILENAME):
        print(f"Mapping file '{MAPPING_FILENAME}' not found.")
        sys.exit(1)

    mappings = load_mapping(MAPPING_FILENAME)
    process_transactions(transactions_path, name_column_number, mappings)


if __name__ == "__main__":
    main()