#!/usr/bin/env python3
import sys
import csv

# Define the expected order of divisions.
EXPECTED_DIVISIONS = ["Sub-Junior", "Junior", "M1", "M2", "M3", "Open"]


def get_division_rank(division):
    """
    Return the ranking of the division based on the expected order.
    Lower numbers indicate a 'lower' division.
    Any division not in the expected list receives a rank lower than Open.
    """
    if division in EXPECTED_DIVISIONS:
        return EXPECTED_DIVISIONS.index(division)
    else:
        # unexpected divisions get a rank lower (i.e. worse)
        return len(EXPECTED_DIVISIONS)


def parse_csv(filepath):
    """
    Reads the CSV and returns a dictionary of unique athletes (keyed by name).
    For lifters appearing in multiple divisions, only the record in the lower (better)
    division (as determined by get_division_rank) is kept.
    Note: The "Place" column is completely ignored.
    """
    athletes_by_name = {}

    with open(filepath, newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            name = row.get("Name", "").strip()
            if not name:
                continue

            division = row.get("Division", "").strip()
            current_rank = get_division_rank(division)

            # If athlete already exists, retain only the record from the lower ranked division.
            if name in athletes_by_name:
                existing_division = athletes_by_name[name].get(
                    "Division", "").strip()
                existing_rank = get_division_rank(existing_division)
                if current_rank < existing_rank:
                    athletes_by_name[name] = row
            else:
                athletes_by_name[name] = row
    return athletes_by_name


def group_athletes(athletes_by_name):
    """
    Group athletes by (Sex, WeightClassKg, Division).
    """
    groups = {}
    for athlete in athletes_by_name.values():
        sex = athlete.get("Sex", "").strip()
        weightclass = athlete.get("WeightClassKg", "").strip()
        division = athlete.get("Division", "").strip()
        key = (sex, weightclass, division)
        groups.setdefault(key, []).append(athlete)
    return groups


def group_sort_key(key):
    """
    Sort groups by:
      - Sex (alphabetically, case-insensitive),
      - WeightClassKg (numerically if possible),
      - Division rank (using get_division_rank).
    """
    sex, weightclass, division = key
    try:
        weight = float(weightclass)
    except ValueError:
        weight = weightclass  # fallback to the string if conversion fails
    return (sex.lower(), str(weight), get_division_rank(division))


def print_group_metric_table(group_key, athletes, metric, metric_label):
    """
    For the given group and metric:
      - Sort athletes by the chosen metric descending and by BodyweightKg ascending (lighter lifter wins on tie).
      - Select the top 3 athletes.
      - Print a header and the table.
    """
    sex, weightclass, division = group_key

    # Sorting key: primary is the metric (descending) and secondary is BodyweightKg (ascending).
    def sort_key(athlete):
        try:
            metric_val = float(athlete.get(metric, 0))
        except ValueError:
            metric_val = 0.0
        try:
            bodyweight = float(athlete.get("BodyweightKg", 0))
        except ValueError:
            bodyweight = 0.0
        return (-metric_val, bodyweight)

    sorted_athletes = sorted(athletes, key=sort_key)
    top_athletes = sorted_athletes[:3]

    # Print header for this table.
    print("\n" + "-" * 50)
    print(f"Top 3 {sex} {weightclass} {division} {metric_label.upper()}")
    print("-" * 50)

    # Define table header.
    header = ["Name", "Division", "Sex", "WeightClassKg", "BodyweightKg",
              "Best3SquatKg", "Best3BenchKg", "Best3DeadliftKg", "TotalKg"]
    header_format = "{:<20} {:<12} {:<8} {:<15} {:<12} {:<14} {:<14} {:<18} {:<10}"
    print(header_format.format(*header))

    for athlete in top_athletes:
        print(header_format.format(
            athlete.get("Name", "").strip(),
            athlete.get("Division", "").strip(),
            athlete.get("Sex", "").strip(),
            athlete.get("WeightClassKg", "").strip(),
            athlete.get("BodyweightKg", "").strip(),
            athlete.get("Best3SquatKg", "").strip(),
            athlete.get("Best3BenchKg", "").strip(),
            athlete.get("Best3DeadliftKg", "").strip(),
            athlete.get("TotalKg", "").strip()
        ))


def main():
    # Ensure the CSV filepath is provided as a command-line argument.
    if len(sys.argv) < 2:
        print("Usage: python separate_athletes.py <csv_filepath>")
        sys.exit(1)

    filepath = sys.argv[1]

    # Parse CSV and deduplicate athletes.
    athletes_by_name = parse_csv(filepath)

    # Group athletes by (Sex, WeightClassKg, Division).
    groups = group_athletes(athletes_by_name)

    # Sort group keys for predictable order.
    sorted_group_keys = sorted(groups.keys(), key=group_sort_key)

    # Define the metrics (in the order required) along with their friendly labels.
    # The order is: Squat, Bench, Deadlift, Total.
    metrics = [
        ("Best3SquatKg", "squat"),
        ("Best3BenchKg", "bench"),
        ("Best3DeadliftKg", "deadlift"),
        ("TotalKg", "total")
    ]

    # For each group, print the top 3 for each metric.
    for group_key in sorted_group_keys:
        athletes = groups[group_key]
        # Print a separator between different groups.
        print("\n" + "=" * 70)
        print(f"Category: {group_key[0]} {group_key[1]} {group_key[2]}")
        print("=" * 70 + "\n")

        for metric, metric_label in metrics:
            print_group_metric_table(group_key, athletes, metric, metric_label)


if __name__ == "__main__":
    main()
