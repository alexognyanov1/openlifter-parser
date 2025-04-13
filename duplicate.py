import csv
import sys
from collections import defaultdict


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 find_duplicates.py <csv_filepath>")
        sys.exit(1)
    filepath = sys.argv[1]
    # Dictionary to collect divisions for each athlete (using Name and Sex as identifier)
    athletes_divisions = defaultdict(set)

    # Open CSV file with UTF-8 encoding and skip comment lines (starting with //)
    with open(filepath, encoding='utf-8-sig') as csvfile:
        lines = [line for line in csvfile if not line.lstrip().startswith('//')]
        reader = csv.DictReader(lines)
        for row in reader:
            name = row.get("Name", "").strip()
            sex = row.get("Sex", "").strip()
            division = row.get("Division", "").strip()
            if name and sex and division:
                key = (name, sex)
                athletes_divisions[key].add(division)

    # Filter athletes that appear in more than one division
    duplicates = {key: sorted(
        divisions) for key, divisions in athletes_divisions.items() if len(divisions) > 1}

    if not duplicates:
        print("No athletes found in multiple divisions.")
        return

    # Pretty print the result as a table
    header = "{:<25} {:<10} {}".format("Name", "Sex", "Divisions")
    print(header)
    print("-" * len(header))
    for (name, sex), divisions in sorted(duplicates.items()):
        divisions_str = ", ".join(divisions)
        print("{:<25} {:<10} {}".format(name, sex, divisions_str))


if __name__ == '__main__':
    main()
