# O2CM Quote Scraper

## Dependencies

1. Python 3 - [get it here](https://www.python.org/downloads/)
2. Python libraries, install them with `pip install -r requirements.txt`

## Usage

Once you install the required dependencies above, the quickest way to get started is to run the program in "auto" mode. You can do this by running `python registration.py auto` and entering your O2CM event ID and the start date for the report. As I'm sure you'd like more information on what's going on, I implore you to read on!

This program needs a few competitor reports from O2CM to work properly. You can either have them fetched automatically or point it at local files that you've downloaded manually. The two methods are detailed below.

Regardless of the mode used, the script will save all the team quotes to the `target` directory, a list of competitor numbers to `numbers.csv`, and open dancer information to `open_dancers.csv`.

### Automatically Download Reports

You can either run the program in auto mode like so:

```shell
python registration.py auto
```

and it will prompt you for necessary info, or you can provide it upfront like so:

```shell
python registration auto --event-id EVENT_ID --after-date AFTER_DATE
```

The script will then fetch all the required reports, parse and process them, and save the results. The reports it fetched will also be saved as `.html` files in the working directory. Feel free to provide these to the manual mode later if you wish to rerun the program.

### Manually Download Reports

So you wish to forage for your own data! To begin, head over to [the O2CM admin login page](https://admin.o2cm.com) and login. Make sure "Reports" is selected in the "take me to" dropdown.

![O2CM login](images/login.png)

Once you're logged in, we will need to download three reports. The first is "Competitors By School", the second is "Entries by Date", and the third is "Competitors By Number".

![O2CM reports page step 1](images/reports_page_1.png)

![O2CM reports page step 2](images/reports_page_2.png)

![O2CM reports page step 3](images/reports_page_3.png)

For each, click "Generate Tabular Report" and save the page to the same directory as this program. On Windows do it with `ctrl+s` and on Mac do it with `cmd+s`. On Linux figure it out. The saved filenames can be whatever you want! *At this point, please stand up, stretch, and drink water. You're doing great.*

If you haven't already, install the Python dependencies by getting into the terminal, navigating to the program directory, and running `python -m pip install -r requirements.txt`. You may need to use `python3` instead of `python` if your `python` installation defaults to Python 2 or older - you can check by running `python --version`.

Finally run the program with `python registration.py files <by school file> <by date file> <by number file>`.
