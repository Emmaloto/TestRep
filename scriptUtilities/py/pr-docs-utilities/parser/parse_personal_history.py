import csv
import re
import argparse
import os

FIELDS = [
    "Title",
    "From (YYYY/MM)",
    "To (YYYY/MM)",
    "Activity",
    "City/town and country/territory",
    "Status in country or territory",
    "Name of company, employer, school, facility (as applicable)"
]

FIELD_PATTERN = re.compile(
    r"(From \(YYYY/MM\)|To \(YYYY/MM\)|Activity|City/town and country/territory|"
    r"Status in country or territory|Name of company, employer, school, facility \(as applicable\))",
    re.IGNORECASE
)

TITLE_PATTERN = re.compile(r"(Personal history \d+)", re.IGNORECASE)


def remove_noise(text):
    # Remove |-- X/17 ... --| blocks (multiline-safe)
    text = re.sub(r"\|\--\s*\d+/\d+\s*--\|", " ", text, flags=re.DOTALL)

    # Remove stray markers
    text = re.sub(r"\|\--.*?\n", " ", text)
    text = re.sub(r"--\|", " ", text)

    # Remove "Remove"
    text = re.sub(r"\bRemove\b", " ", text, flags=re.IGNORECASE)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def parse_blocks(text):
    records = []

    # Split while keeping delimiters
    parts = re.split(r"(Personal history \d+)", text, flags=re.IGNORECASE)

    # parts will look like: ["", "Personal history 9", " block text...", "Personal history 10", " block..."]

    for i in range(1, len(parts), 2):
        title = parts[i].strip()
        block = parts[i + 1] if i + 1 < len(parts) else ""

        record = {field: "" for field in FIELDS}
        record["Title"] = title

        matches = list(FIELD_PATTERN.finditer(block))

        for idx, match in enumerate(matches):
            field_name = match.group(0)

            start = match.end()
            end = matches[idx + 1].start() if idx + 1 < len(matches) else len(block)

            value = block[start:end].strip()
            value = re.sub(r"\s+", " ", value)

            for f in FIELDS:
                if f.lower() == field_name.lower():
                    record[f] = value
                    break

        records.append(record)

    return records


def write_csv(records, output_file):
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(records)


def main():
    parser = argparse.ArgumentParser(description="Parse Personal History text into CSV")
    parser.add_argument("input", help="Input .txt file")
    parser.add_argument("-o", "--output", help="Output CSV file (optional)")

    args = parser.parse_args()

    input_file = args.input
    output_file = args.output

    if not output_file:
        base = os.path.splitext(input_file)[0]
        output_file = base + ".csv"

    with open(input_file, "r", encoding="utf-8") as f:
        raw_text = f.read()

    cleaned_text = remove_noise(raw_text)
    records = parse_blocks(cleaned_text)
    write_csv(records, output_file)

    print(f"Extracted {len(records)} records → {output_file}")


if __name__ == "__main__":
    main()

    
    # Example usage:
    # python parse_personal_history.py personal_history.txt -o personal_history.csv
    # python parse_personal_history.py "G:\My Drive\General Immigration Docs\Canada Docs\Spousal Sponsorship\(1) Spousal Sponsorship Final - Personal App\Forms\Online Forms\Schedule A - Background_Declaration Section D - Personal history.txt" -o personal_history.csv