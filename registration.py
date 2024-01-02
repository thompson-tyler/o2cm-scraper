import pandas as pd
import sys
import os


SEPTEMBER = 9
OCTOBER = 10
NOVEMBER = 11

EARLY_REG_PRICE = 40
REG_PRICE = 45
# This is the last day of EARLY_REG_PRICE, after this day the price goes up to REG_PRICE
EARLY_REG_CUTOFF_MONTH = OCTOBER
EARLY_REG_CUTOFF_DAY = 19

TARGET_DIR = "./target"


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
    # This is kinda wacky but it works so long as the number of days in a month doesn't exceed 31
    if (month * 32) + day <= (EARLY_REG_CUTOFF_MONTH * 32) + EARLY_REG_CUTOFF_DAY:
        return EARLY_REG_PRICE
    return REG_PRICE


# Output a pandas table to both an excel and csv file in the target directory
# Files will be named <name>.xlsx and <name>.csv
def output_table(table, name):
    table.to_excel(in_target_dir(f"{name}.xlsx"), index=False)
    table.to_csv(in_target_dir(f"{name}.csv"), index=False)


def main():
    if len(sys.argv) == 4:
        by_school_filename = verify_file(sys.argv[1])
        by_date_filename = verify_file(sys.argv[2])
        by_number_filename = verify_file(sys.argv[3])
    else:
        by_school_filename = input('Enter the "Competitor By School" filename: ')
        by_date_filename = input('Enter the "Entries by Date" filename: ')
        by_number_filename = input('Enter the "Competitor By Number" filename: ')

    by_school_table = pd.read_html(by_school_filename, header=0)[0]
    by_date_table = pd.read_html(by_date_filename, header=0)[0]
    by_number_table = pd.read_html(by_number_filename, header=0)[0]

    # Reverse order of by_date_table so that earlier dates come first
    # Done so that participants' earliest registration dates are used for pricing
    by_date_table = by_date_table.iloc[::-1]

    # Join first and last names in the by_number_table to make things easier
    by_number_table["Full Name"] = (
        by_number_table["First"] + " " + by_number_table["Last"]
    )

    if not os.path.isdir(TARGET_DIR):
        print(f"Creating directory: {TARGET_DIR}")
        os.mkdir(TARGET_DIR)

    # Takes a table of dancers from a single school and processes it, outputting the results
    # to both an excel and csv file in the target directory
    def process_reg_table(reg_table, school_name):
        print(f"Processing {school_name}")

        has_registered = False

        for index, (first_name, last_name) in enumerate(
            zip(reg_table["First"], reg_table["Last"])
        ):
            name = f"{first_name} {last_name}"

            # Find dancer's entry in either the leader or follower column
            if name in list(by_date_table["Leader"]):
                entry = by_date_table.loc[by_date_table["Leader"] == name]
            elif name in list(by_date_table["Follow"]):
                entry = by_date_table.loc[by_date_table["Follow"] == name]
            else:
                # Skip and log dancers who are under a school but not registered in a style
                print(f"> {name} Not registered in any styles?")
                reg_table.loc[index, "Pass"] = "NO STYLES"
                continue

            # Get their number, if they have one, and set it in the reg_table
            num_cell = by_number_table.loc[
                by_number_table["Full Name"] == name, "Number"
            ]
            if num_cell.empty:
                number = ""
            else:
                number = str(num_cell.values[0])
            reg_table.loc[index, "Number"] = number

            # Extract the date from the entry
            date = list(entry["Date"])[0].split("-")
            month = int(date[1])
            day = int(date[2])

            # Set the price for the dancer's entry
            reg_table.loc[index, "Pass"] = get_reg_price(month, day)

            has_registered = True

        if not has_registered:
            print(f"> No dancers from {school_name}")
            return

        # Concat first and last name columns into a single column "Full Name"
        reg_table.insert(2, "Full Name", "")
        reg_table["Full Name"] = reg_table["First"] + " " + reg_table["Last"]
        reg_table = reg_table.drop(columns=["First", "Last"])

        # Remove index column
        reg_table = reg_table.drop(columns=["index"])

        output_table(reg_table, school_name)

    # Processes each school. list(set()) removes duplicates
    for school in list(set(by_school_table["school"])):
        school_reg = (
            by_school_table[by_school_table["school"] == school].copy().reset_index()
        )
        process_reg_table(school_reg, school)

    # Processes unasigned dancers
    unaffil_reg = (
        by_school_table[pd.isnull(by_school_table["school"])].copy().reset_index()
    )
    unaffil_reg = unaffil_reg.drop(columns=["school"])
    process_reg_table(unaffil_reg, "Unaffiliated dancers")

    # Shit out the numbers
    by_number_table["Number"].to_csv("numbers.csv", index=False)


if __name__ == "__main__":
    main()
