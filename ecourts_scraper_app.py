import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta

BASE_URL = "https://services.ecourts.gov.in/ecourtindia_v6/"
CASE_SEARCH_URL = BASE_URL + "?p=casestatus/index/"

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
            return {"error": "Case details not found or invalid input."}

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
        return f"✅ Listed Today ({listing_date})"
    elif listing_date == tomorrow:
        return f"🕒 Listed Tomorrow ({listing_date})"
    else:
        return f"❌ Not listed today or tomorrow (Next: {listing_date})"


#UI

st.set_page_config(page_title="eCourts Scraper", page_icon="⚖️", layout="centered")

st.title("⚖️ eCourts Scraper")
st.write("Fetch court case details and check if a case is listed today or tomorrow.")

# Input choice
search_type = st.radio("Search by:", ["CNR Number", "Case Type + Number + Year"])

if search_type == "CNR Number":
    cnr = st.text_input("Enter CNR Number (Example: MHJK010000002023)")
    case_type = case_no = case_year = None
else:
    cnr = None
    case_type = st.text_input("Enter Case Type (e.g., CR, CS, CC)")
    case_no = st.text_input("Enter Case Number")
    case_year = st.text_input("Enter Case Year (e.g., 2023)")

if st.button("🔍 Search Case"):
    with st.spinner("Fetching case details..."):
        try:
            soup = fetch_case_html(cnr, case_type, case_no, case_year)
            case_info = parse_case_details(soup)
            if "error" in case_info:
                st.error(case_info["error"])
            else:
                listing_status = check_listing_date(case_info)
                st.success("Case details fetched successfully!")
                st.subheader("📄 Case Information")
                st.json(case_info)
                st.info(listing_status)

                # Save result locally
                result = {
                    "listing_status": listing_status,
                    "details": case_info,
                    "timestamp": str(datetime.now())
                }
                with open("case_result.json", "w") as f:
                    json.dump(result, f, indent=4)
                st.download_button(
                    label="📥 Download Result (JSON)",
                    data=json.dumps(result, indent=4),
                    file_name="case_result.json",
                    mime="application/json"
                )
        except Exception as e:
            st.error(f"Error fetching case details: {e}")

st.divider()
st.caption("Developed by Ankit Raj Jha • Intern Task Submission")
