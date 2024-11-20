import pandas as pd
import os
import argparse
import re

from reports import *


SEPTEMBER = 9
OCTOBER = 10
NOVEMBER = 11

EARLY_REG_PRICE = 40
REG_PRICE = 45
# This is the last day of EARLY_REG_PRICE, after this day the price goes up to REG_PRICE
EARLY_REG_CUTOFF_MONTH = OCTOBER
EARLY_REG_CUTOFF_DAY = 19

TARGET_DIR = "./target"
DEFAULT_BY_SCHOOL_FILENAME = "by_school.html"
DEFAULT_BY_NUMBER_FILENAME = "by_number.html"
DEFAULT_BY_DATE_FILENAME = "by_date.html"

OPEN_KEYWORDS = ["open", "champ"]
OPEN_KEYWORDS_CASE_SENSITIVE = False

DATE_REGEX = r"(\d{4})-(\d{2})-(\d{2})"


def build_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(required=True, dest="mode")

    auto_parser = subparsers.add_parser(
        "auto", help="Automatically fetch reports from O2CM."
    )
    auto_parser.add_argument("--event-id", "-e", help="The event ID.")
    auto_parser.add_argument(
        "--after-date",
        "-d",
        help="The date after which to fetch entries (YYYY-MM-DD).",
    )

    file_parser = subparsers.add_parser(
        "files",
        help="Use local files as input. They must be HTML files from O2CM.",
    )
    file_parser.add_argument(
        "by_school_filename",
        help='The "Competitors By School" report filename.',
    )
    file_parser.add_argument(
        "by_date_filename",
        help='The "Entries by Date report" filename.',
    )
    file_parser.add_argument(
        "by_number_filename",
        help='The "Competitors By Number" report filename.',
    )

    return parser


def verify_file(filename):
    if not os.path.isfile(filename):
        print(f"Unknown file: {filename}")
        exit(1)
    return filename


def in_target_dir(filename):
    return os.path.join(TARGET_DIR, filename)


# Return true if the given month and day are before the early registration cutoff
# month and day are expected to be integers in the range [1, 12] and [1, 31] respectively
def get_reg_price(month, day):
    assert 1 <= month <= 12
    assert 1 <= day <= 31
    # This is kinda wacky but it works so long as the number of days in a month doesn't exceed 31
    if (month * 32) + day <= (
        EARLY_REG_CUTOFF_MONTH * 32
    ) + EARLY_REG_CUTOFF_DAY:
        return EARLY_REG_PRICE
    return REG_PRICE


# Output a pandas table to both an excel and csv file in the target directory
# Files will be named <name>.xlsx and <name>.csv
def save_school_reg(table, name):
    table.to_excel(in_target_dir(f"{name}.xlsx"), index=False)
    table.to_csv(in_target_dir(f"{name}.csv"), index=False)


def main():

    ### Acquire input files and prepare output directory ###

    parser = build_parser()
    args = parser.parse_args()

    if args.mode == "files":
        by_school_filename = verify_file(args.by_school_filename)
        by_date_filename = verify_file(args.by_date_filename)
        by_number_filename = verify_file(args.by_number_filename)
    elif args.mode == "auto":
        event_id = args.event_id or input("Event ID: ")
        after_date = args.after_date or input(
            "Date after which to fetch entries (YYYY-MM-DD): "
        )
        if not re.match(DATE_REGEX, after_date):
            print("Invalid date format. Must be YYYY-MM-DD")
            exit(1)

        by_school_html = fetch_by_school_report(event_id)
        print("Successfully fetched by_school report")
        with open(DEFAULT_BY_SCHOOL_FILENAME, "w") as f:
            f.write(by_school_html)

        by_number_html = fetch_by_number_report(event_id)
        print("Successfully fetched by_number report")
        with open(DEFAULT_BY_NUMBER_FILENAME, "w") as f:
            f.write(by_number_html)

        by_date_html = fetch_by_date_report(event_id, after_date)
        print("Successfully fetched by_date report")
        with open(DEFAULT_BY_DATE_FILENAME, "w") as f:
            f.write(by_date_html)

        by_school_filename = DEFAULT_BY_SCHOOL_FILENAME
        by_number_filename = DEFAULT_BY_NUMBER_FILENAME
        by_date_filename = DEFAULT_BY_DATE_FILENAME
    else:
        print("Unknown mode")
        exit(1)

    # If the html we got doesn't parse, then it's probably because the tables were empty
    # In that case, create empty tables
    try:
        by_school_table = pd.read_html(by_school_filename, header=0)[0]
    except ValueError:
        by_school_table = pd.DataFrame(columns=["First", "Last", "school"])
        print(f"WARNING: couldn't parse entries from {by_school_filename}")
    try:
        by_number_table = pd.read_html(by_number_filename, header=0)[0]
    except ValueError:
        by_number_table = pd.DataFrame(columns=["First", "Last", "Number"])
        print(f"WARNING: couldn't parse entries from {by_number_filename}")
    try:
        by_date_table = pd.read_html(by_date_filename, header=0)[0]
    except ValueError:
        by_date_table = pd.DataFrame(
            columns=["Date", "Event", "Leader", "Follow"]
        )
        print(f"WARNING: couldn't parse entries from {by_date_filename}")

    # Create target directory if it doesn't exist
    if not os.path.isdir(TARGET_DIR):
        print(f"Creating directory: {TARGET_DIR}")
        os.mkdir(TARGET_DIR)
    # If it does exist, remove old files
    else:
        print(f"Directory {TARGET_DIR} already exists. Removing old files...")
        for file in os.listdir(TARGET_DIR):
            os.remove(os.path.join(TARGET_DIR, file))

    ### Preprocess tables ###

    # Reverse order of by_date_table so that earlier dates come first
    # Done so that participants' earliest registration dates are used for pricing
    by_date_table = by_date_table.iloc[::-1]

    # Join first and last names in the by_school_table and by_number_table to make things easier
    by_school_table["Full Name"] = (
        by_school_table["First"] + " " + by_school_table["Last"]
    )
    by_number_table["Full Name"] = (
        by_number_table["First"] + " " + by_number_table["Last"]
    )
    by_school_table = by_school_table.drop(columns=["First", "Last"])
    by_number_table = by_number_table.drop(columns=["First", "Last"])

    # Set null schools to "Unaffiliated"
    by_school_table["school"] = by_school_table["school"].fillna("Unaffiliated")

    # Remove TBA entries
    print(by_school_table)
    # Ensure "Full Name" column contains only strings
    by_school_table["Full Name"] = by_school_table["Full Name"].astype(str)
    by_school_table = by_school_table[
        ~by_school_table["Full Name"].str.startswith("TBA")
    ]

    # Add Number column to by_school_table
    by_school_table["Number"] = None

    ### Process tables ###

    # Blank dict to store open dancers. Will be converted to a DataFrame later
    open_dancers = {
        "Full Name": [],
        "Number": [],
        "school": [],
    }

    # Processes each school. list(set()) removes duplicates
    for school_name in list(set(by_school_table["school"])):
        print(f"Processing {school_name}")

        has_registered = False

        school_reg = (
            by_school_table[by_school_table["school"] == school_name]
            .copy()
            .reset_index()
        )

        for index, name in enumerate(school_reg["Full Name"]):
            # Find dancer's entry in either the leader or follower column
            if (by_date_table["Leader"] == name).any():
                entry = by_date_table.loc[by_date_table["Leader"] == name]
            elif (by_date_table["Follow"] == name).any():
                entry = by_date_table.loc[by_date_table["Follow"] == name]
            else:
                # Skip dancers who are under a school but not registered in a style
                school_reg.loc[index, "Pass"] = "NO STYLES"
                continue

            # Get their number, if they have one, and set it in the school_reg
            num_cell = by_number_table[by_number_table["Full Name"] == name][
                "Number"
            ]
            if not num_cell.empty:
                school_reg.loc[index, "Number"] = str(num_cell.iloc[0])

            # Determine if the dancer is only registered for open events
            all_open = (
                by_date_table[
                    (by_date_table["Leader"] == name)
                    | (by_date_table["Follow"] == name)
                ]["Event"]
                .str.contains(
                    "|".join(OPEN_KEYWORDS), case=OPEN_KEYWORDS_CASE_SENSITIVE
                )
                .all()
            )
            # Insert them into the open_dancers table and mark their pass as "OPEN"
            if all_open:
                open_dancers["Full Name"].append(name)
                open_dancers["school"].append(school_name)
                open_dancers["Number"].append(school_reg.loc[index, "Number"])
                school_reg.loc[index, "Pass"] = "OPEN"
            # Otherwise, set their pass price based on their earliest registration date
            else:
                # Extract the date from the entry
                date = entry["Date"].iloc[0].split("-")
                month = int(date[1])
                day = int(date[2])

                # Set the price for the dancer's entry
                school_reg.loc[index, "Pass"] = get_reg_price(month, day)

            has_registered = True

        if not has_registered:
            print(f"> No dancers from {school_name}")

        # Remove index column
        school_reg = school_reg.drop(columns=["index"])

        save_school_reg(school_reg, school_name)

    # Shit out the numbers
    by_number_table["Number"].to_csv("numbers.csv", index=False)

    # Produce the open dancers
    pd.DataFrame(open_dancers).to_csv("open_dancers.csv", index=False)


if __name__ == "__main__":
    main()
