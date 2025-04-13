#!/usr/bin/env python3
"""
This script parses an OpenLifter-exported CSV file and outputs the top 3 athletes
for each age and weight category.

It assumes that the CSV file has at least the following columns (default names):
    - Age category (default column name: 'AgeCategory')
    - Weight category (default column name: 'WeightCategory')
    - Score (or total lifted weight) used for ranking (default column name: 'Total')

You can override these defaults with command-line parameters if your file uses different headers,
or if you need to specify a different encoding or delimiter.

Usage example:
    python top3_openlifter.py "протокол 2 жени-ветерани .csv" --age_col "AgeCategory" --weight_col "WeightCategory" --score_col "Total" --encoding "utf-8" --sep ","
    
If your file uses a different encoding (e.g., cp1251) or delimiter (e.g., semicolon), adjust the parameters accordingly.
"""

import pandas as pd
import sys
import argparse


def main():
    # Set up argument parsing to allow custom file paths and column specifications.
    parser = argparse.ArgumentParser(
        description='Parse OpenLifter exported results and list the top 3 athletes per age and weight category.'
    )
    parser.add_argument(
        'csv_file', help='Path to the OpenLifter exported CSV file.')
    parser.add_argument('--age_col', default='Division',
                        help='Column name for the age category (default: Division)')
    parser.add_argument('--weight_col', default='WeightClassKg',
                        help='Column name for the weight category (default: WeightClassKg)')
    parser.add_argument('--score_col', default='TotalKg',
                        help='Column name for the score or total lift (default: TotalKg)')
    parser.add_argument('--encoding', default='utf-8',
                        help='Encoding used to read the CSV file (default: utf-8)')
    parser.add_argument('--sep', default=',',
                        help='Delimiter used in the CSV file (default: ",")')

    args = parser.parse_args()

    print(args)

    # Try reading the CSV file. If there is an error (e.g. wrong encoding or delimiter), it will raise an exception.
    try:
        df = pd.read_csv(args.csv_file, encoding=args.encoding, sep=args.sep)
    except Exception as e:
        print(f"Error reading CSV file {args.csv_file}: {e}")
        sys.exit(1)

    # Print out the column names detected in the CSV file. This helps verify your file structure.
    print("Columns detected in the CSV file:")
    print(df.columns.tolist())

    # Check that the CSV file contains the required columns.
    required_columns = [args.age_col, args.weight_col, args.score_col]
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        print(
            f"Missing required columns in CSV file: {missing_cols}. Please verify the column names or adjust the parameters.")
        sys.exit(1)

    # Group by age and weight category.
    grouped = df.groupby([args.age_col, args.weight_col])

    # Define a helper function that sorts each group by the score column in descending order
    # (assuming higher score/best performance is better) and then selects the top 3.
    def get_top3(group):
        return group.sort_values(by=args.score_col, ascending=False).head(3)

    # Apply the function to each group.
    top3_df = grouped.apply(get_top3).reset_index(drop=True)

    # Print the results.
    print("\nTop 3 athletes for each age and weight category:")
    print(top3_df)

    # Optionally, if you want to save the output to a new CSV file, uncomment the line below:
    # top3_df.to_csv("top3_results.csv", index=False)


if __name__ == '__main__':
    main()
