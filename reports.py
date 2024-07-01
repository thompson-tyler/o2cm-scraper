import requests

REPORTS_BASE_URL = "https://admin.o2cm.com/Reports/tabular.aspx"
BY_SCHOOL_REPNO = 11
BY_NUMBER_REPNO = 15
BY_DATE_REPNO = 83


def fetch_by_school_report(event_id):
    res = requests.get(
        REPORTS_BASE_URL,
        params={"repno": BY_SCHOOL_REPNO},
        cookies={
            "EventID": event_id,
            "szTitle": "",  # The title of the report. The server errors if it's not present
        },
    )
    if res.status_code != 200:
        print("Failed to fetch by school report")
        exit(1)
    return res.text


def fetch_by_number_report(event_id):
    res = requests.get(
        REPORTS_BASE_URL,
        params={"repno": BY_NUMBER_REPNO},
        cookies={
            "EventID": event_id,
            "szTitle": "",  # The title of the report. The server errors if it's not present
        },
    )
    if res.status_code != 200:
        print("Failed to fetch by number report")
        exit(1)
    return res.text


def fetch_by_date_report(event_id, date_after):
    res = requests.get(
        REPORTS_BASE_URL,
        params={"repno": BY_DATE_REPNO, "repText": date_after},
        cookies={
            "EventID": event_id,
            "szTitle": "",  # The title of the report. The server errors if it's not present
        },
    )
    if res.status_code != 200:
        print("Failed to fetch by date report")
        exit(1)
    return res.text
