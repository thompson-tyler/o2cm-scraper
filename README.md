# O2CM Quote Scraper

## Dependencies

1. `python 3` - [get it here](https://www.python.org/downloads/)
2. Python libraries, install them with `pip install -r requirements.txt`

## Usage

Next we must collect that sweet succulent data. Head over to [the O2CM admin login page](https://admin.o2cm.com) and login. Make sure "Reports" is selected in the "take me to" dropdown.

![O2CM login](images/login.png)

Once you're logged in, we will need to download three reports. The first is "Competitors By School", the second is "Entries by Date", and the third is "Competitors By Number".

![O2CM reports page step 1](images/reports_page_1.png)

![O2CM reports page step 2](images/reports_page_2.png)

![O2CM reports page step 3](images/reports_page_3.png)

For each, click "Generate Tabular Report" and save the page to the same directory as this program. On Windows do it with `ctrl+s` and on Mac do it with `cmd+s`. On Linux figure it out. The saved filenames can be whatever you want! *At this point, please stand up, stretch, and drink water. You're doing great.*

If you haven't already, install the Python dependencies by getting into the terminal, navigating to the program directory, and running `python -m pip install -r requirements.txt`. If you're on Mac or Linux, you may need to use `python3` instead of `python`.

Finally run the program with `python registration.py <by school file> <by date file> <by number file>`. Alternatively, run it with `python registration.py` and it will prompt you for the filenames. The program will output a bunch of quotes to the `target` directory and all the competitor numbers to `numbers.csv`.
