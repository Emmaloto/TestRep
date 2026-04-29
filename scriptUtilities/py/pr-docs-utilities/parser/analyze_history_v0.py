import csv
import argparse
import os
from datetime import datetime

DATE_FMT = "%Y/%m"


# ---------- Utilities ----------

def parse_date(date_str):
    return datetime.strptime(date_str.strip(), DATE_FMT)


def format_date(dt):
    return dt.strftime("%Y/%m")


def month_diff(start, end):
    return (end.year - start.year) * 12 + (end.month - start.month)


def entry_label(entry):
    name = entry["raw"].get(
        "Name of company, employer, school, facility (as applicable)", ""
    ).strip()

    return f"{entry['title']} | {name} ({format_date(entry['from'])} → {format_date(entry['to'])})"


# ---------- Load Data ----------

def load_csv(file_path):
    entries = []

    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            try:
                entry = {
                    "title": row.get("Title", "").strip(),
                    "from": parse_date(row["From (YYYY/MM)"]),
                    "to": parse_date(row["To (YYYY/MM)"]),
                    "raw": row
                }
                entries.append(entry)
            except Exception as e:
                print(f"Skipping invalid row: {row} ({e})")

    return entries


# ---------- Core Analysis ----------

def find_invalid_ranges(entries):
    return [e for e in entries if e["from"] > e["to"]]


def get_span(entries):
    start = min(e["from"] for e in entries)
    end = max(e["to"] for e in entries)
    return start, end


def merge_intervals(entries):
    """Create union of all time coverage"""
    intervals = sorted([(e["from"], e["to"]) for e in entries], key=lambda x: x[0])
    merged = []

    for start, end in intervals:
        if not merged:
            merged.append([start, end])
        else:
            last_start, last_end = merged[-1]

            if start <= last_end:
                merged[-1][1] = max(last_end, end)
            else:
                merged.append([start, end])

    return merged


def find_true_gaps(merged_intervals):
    gaps = []

    for i in range(len(merged_intervals) - 1):
        end_current = merged_intervals[i][1]
        start_next = merged_intervals[i + 1][0]

        if start_next > end_current:
            gaps.append((end_current, start_next))

    return gaps


def find_pairwise_gaps(entries):
    """Gaps between sorted entries (even if covered elsewhere)"""
    entries_sorted = sorted(entries, key=lambda x: x["from"])
    gaps = []

    for i in range(len(entries_sorted) - 1):
        a = entries_sorted[i]
        b = entries_sorted[i + 1]

        if b["from"] > a["to"]:
            gaps.append((a, b))

    return gaps


def is_gap_covered(gap_start, gap_end, merged_intervals):
    """Check if gap is actually covered by any merged interval"""
    for start, end in merged_intervals:
        if start <= gap_start and end >= gap_end:
            return True
    return False


def ranges_overlap(a, b):
    return a["from"] < b["to"] and b["from"] < a["to"]


def find_overlaps(entries):
    overlaps = []

    for i in range(len(entries)):
        for j in range(i + 1, len(entries)):
            if ranges_overlap(entries[i], entries[j]):
                overlaps.append((entries[i], entries[j]))

    return overlaps


# ---------- Reporting ----------

def generate_report(entries, invalid, merged, true_gaps, pairwise_gaps, overlaps, span):
    lines = []

    start, end = span
    total_months = month_diff(start, end)

    lines.append("# Personal History Analysis Report\n")

    # Span
    lines.append("## 📊 Timeline Span")
    lines.append(f"- **From:** {format_date(start)}")
    lines.append(f"- **To:** {format_date(end)}")
    lines.append(f"- **Total Duration:** ~{total_months} months\n")

    # Invalid ranges
    lines.append("## ❌ Invalid Date Ranges (From > To)")
    if not invalid:
        lines.append("✅ None\n")
    else:
        for e in invalid:
            lines.append(f"- {entry_label(e)}")
        lines.append("")

    # True gaps (real missing time)
    lines.append("## ⚠️ True Gaps (No Coverage At All)")
    if not true_gaps:
        lines.append("✅ No uncovered gaps\n")
    else:
        for g_start, g_end in true_gaps:
            months = month_diff(g_start, g_end)
            emoji = "⚪" if months <= 1 else "🔴"

            lines.append(
                f"- {emoji} {format_date(g_start)} → {format_date(g_end)} ({months} months)"
            )
        lines.append("")

    # Pairwise gaps (contextual)
    lines.append("## ℹ️ Gaps Between Entries (Contextual)")
    if not pairwise_gaps:
        lines.append("✅ None\n")
    else:
        for a, b in pairwise_gaps:
            gap_start = a["to"]
            gap_end = b["from"]
            months = month_diff(gap_start, gap_end)

            covered = is_gap_covered(gap_start, gap_end, merged)

            emoji = "⚪" if months <= 1 else "🟡"

            lines.append(f"- {emoji} {format_date(gap_start)} → {format_date(gap_end)} ({months} months)")
            lines.append(f"  between:")
            lines.append(f"  {entry_label(a)}")
            lines.append(f"  {entry_label(b)}")

            if covered:
                lines.append("  ✅ Covered by overlapping entries")

            lines.append("")

    # Overlaps
    lines.append("## ⚠️ Overlapping Entries")
    if not overlaps:
        lines.append("✅ None\n")
    else:
        for a, b in overlaps:
            lines.append(f"- {entry_label(a)}")
            lines.append(f"  overlaps with")
            lines.append(f"  {entry_label(b)}\n")

    return "\n".join(lines)


# ---------- Main ----------

def main():
    parser = argparse.ArgumentParser(description="Analyze Personal History CSV")
    parser.add_argument("input", help="Input CSV file")
    parser.add_argument("-o", "--output", help="Output markdown file")

    args = parser.parse_args()

    input_file = args.input

    if args.output:
        output_file = args.output
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"report_{timestamp}.md"

    entries = load_csv(input_file)

    if not entries:
        print("No valid entries found.")
        return

    invalid = find_invalid_ranges(entries)
    span = get_span(entries)

    merged = merge_intervals(entries)
    true_gaps = find_true_gaps(merged)
    pairwise_gaps = find_pairwise_gaps(entries)
    overlaps = find_overlaps(entries)

    report = generate_report(
        entries, invalid, merged, true_gaps, pairwise_gaps, overlaps, span
    )

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"Report generated → {output_file}")


if __name__ == "__main__":
    main()
