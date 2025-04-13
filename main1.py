import csv
import sys
from collections import defaultdict

# Define the preferred division order. Divisions not in this dictionary will be assigned a high rank.
division_order = {
    'Sub-Junior': 0,
    'Junior': 1,
    'M1': 2,
    'M2': 3,
    'M3': 4,
    'Open': 5,
}


def safe_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 main1.py <csv_filepath>")
        sys.exit(1)
    filepath = sys.argv[1]
    groups = defaultdict(list)

    # Open CSV file with UTF-8 encoding (sometimes a BOM is present)
    with open(filepath, encoding='utf-8-sig') as csvfile:
        # Remove any comments (lines starting with //) if present
        lines = [line for line in csvfile if not line.lstrip().startswith('//')]
        reader = csv.DictReader(lines)

        for row in reader:
            # Skip row if "Place" is not a number (for example "NS")
            if not row['Place'].strip().isdigit():
                continue
            # Create the key from Division, Sex and WeightClassKg
            key = (
                row['Division'].strip(),
                row['Sex'].strip(),
                row['WeightClassKg'].strip()
            )
            groups[key].append(row)

    # Process each group: sort by TotalKg descending, then by BodyweightKg descending if equal
    result = {}
    for key, athletes in groups.items():
        athletes.sort(key=lambda a: (safe_float(a.get('TotalKg')),
                                     safe_float(a.get('BodyweightKg'))),
                      reverse=True)
        result[key] = athletes

    # Filter out duplicate competitors: if a person (by Name and Sex) appears in multiple groups,
    # only keep him in the lowest division (lowest rank according to division_order)
    unique_athletes = set()
    unique_result = {}
    # Sort groups by the division order, then by Sex and WeightClassKg for consistent ordering.
    for key in sorted(result.keys(),
                      key=lambda k: (division_order.get(k[0], 999), k[1], k[2])):
        filtered = []
        for athlete in result[key]:
            identifier = (athlete['Name'].strip(), athlete['Sex'].strip())
            if identifier not in unique_athletes:
                filtered.append(athlete)
                unique_athletes.add(identifier)
        unique_result[key] = filtered

    # Pretty print output as tables for each group with more newlines between groups.
    for (division, sex, weight_class), athletes in sorted(unique_result.items(),
                                                          key=lambda k: (division_order.get(k[0][0], 999), k[0][1], k[0][2])):
        # Only print non-empty groups
        if not athletes:
            continue
        print("\n\n========================================")
        print(
            f"Group: Division={division}, Sex={sex}, WeightClassKg={weight_class}")
        print("========================================")
        header = f"{'Name':<25} {'TotalKg':>10} {'BodyweightKg':>15}"
        print(header)
        print("-" * len(header))
        for athlete in athletes:
            total = safe_float(athlete.get('TotalKg'))
            bodyweight = safe_float(athlete.get('BodyweightKg'))
            name = athlete.get('Name')
            print(f"{name:<25} {total:10.2f} {bodyweight:15.2f}")
        print("\n")


if __name__ == '__main__':
    main()
