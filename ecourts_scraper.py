import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
import argparse
import os

BASE_URL = "https://services.ecourts.gov.in/ecourtindia_v6/"
CASE_SEARCH_URL = BASE_URL + "?p=casestatus/index/"

# ---------------------- Helper Functions ----------------------

def fetch_case_html(cnr=None, case_type=None, case_no=None, case_year=None):
    """Fetch the raw HTML of case details."""
    session = requests.Session()

    if cnr:
        payload = {"cnrno": cnr}
        url = BASE_URL + "?p=casestatus/case_no"
    else:
        payload = {
            "case_type": case_type,
            "case_no": case_no,
            "case_year": case_year
        }
        url = BASE_URL + "?p=casestatus/case_no"

    response = session.post(url, data=payload, timeout=20)
    response.raise_for_status()
    return BeautifulSoup(response.text, "lxml")


def parse_case_details(soup):
    """Extract case details from the HTML."""
    case_info = {}
    try:
        table = soup.find("table", {"class": "table"})
        if not table:
            return {"error": "Case details not found"}

        rows = table.find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            if len(cols) == 2:
                key = cols[0].text.strip().replace(":", "")
                value = cols[1].text.strip()
                case_info[key] = value
    except Exception as e:
        case_info["error"] = str(e)
    return case_info


def check_listing_date(case_info):
    """Check if the case is listed today or tomorrow."""
    today = datetime.today().date()
    tomorrow = today + timedelta(days=1)

    listing_date = None
    for key, value in case_info.items():
        if "Next Hearing Date" in key or "Listing Date" in key:
            try:
                listing_date = datetime.strptime(value, "%d-%m-%Y").date()
            except ValueError:
                pass

    if not listing_date:
        return "No listing date found."

    if listing_date == today:
        return f"Listed Today ({listing_date})"
    elif listing_date == tomorrow:
        return f"Listed Tomorrow ({listing_date})"
    else:
        return f"Not listed today or tomorrow (Next: {listing_date})"


def find_pdf_link(soup):
    """Find a downloadable PDF link if available."""
    link = soup.find("a", href=lambda h: h and h.endswith(".pdf"))
    return link["href"] if link else None


def download_file(url, filename):
    """Download and save any file from a given URL."""
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open(filename, "wb") as f:
            f.write(r.content)
        return f"Downloaded: {filename}"
    return f"Failed to download: {url}"


def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


#Logic

def main():
    parser = argparse.ArgumentParser(description="eCourts Scraper Tool")
    parser.add_argument("--cnr", help="Search case by CNR number")
    parser.add_argument("--case_type", help="Case type (e.g. CR, CS)")
    parser.add_argument("--case_no", help="Case number")
    parser.add_argument("--case_year", help="Case year")
    parser.add_argument("--causelist", action="store_true", help="Download today's cause list if available")
    args = parser.parse_args()

    if not args.cnr and not (args.case_type and args.case_no and args.case_year):
        print("Provide either CNR or Case Type + Number + Year.")
        return

    print("Fetching case details...")

    soup = fetch_case_html(
        cnr=args.cnr,
        case_type=args.case_type,
        case_no=args.case_no,
        case_year=args.case_year,
    )

    case_info = parse_case_details(soup)
    if "error" in case_info:
        print("Error:", case_info["error"])
        return

    listing_status = check_listing_date(case_info)
    print("Listing Status:", listing_status)

    pdf_link = find_pdf_link(soup)
    if pdf_link:
        print("PDF available. Downloading...")
        filename = f"case_{args.case_no or args.cnr}.pdf"
        print(download_file(pdf_link, filename))
    else:
        print("No case PDF found.")

    output = {
        "listing_status": listing_status,
        "details": case_info,
        "downloaded_pdf": bool(pdf_link)
    }

    save_json(output, "case_result.json")
    print("Case details saved as case_result.json")

    if args.causelist:
        print("Attempting to download today's cause list...")
        cause_list_url = BASE_URL + "?p=casestatus/cause_list"
        try:
            print(download_file(cause_list_url, "cause_list.pdf"))
        except Exception as e:
            print("Cause list not available:", e)


if __name__ == "__main__":
    main()

if __name__ == "__main__":
    # Test mode
    print("Testing scraper connectivity...")
    test_url = "https://services.ecourts.gov.in/ecourtindia_v6/"
    r = requests.get(test_url, timeout=10)
    print("Status Code:", r.status_code)
    print("Page Title:", BeautifulSoup(r.text, "lxml").title.text)
