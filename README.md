**eCourts Scraper – Intern Task**

 **Objective:**

This Python script automates fetching court case details from the eCourts Portal.
It checks whether a case is listed today or tomorrow, extracts its serial number and court name, and optionally downloads the case PDF or today’s cause list.

**#Features:**

  1. Search case by CNR or Case Type + Number + Year
  2. Detect if a case is listed today or tomorrow
  3. Display court name, serial number, and hearing dat
  4. Optional PDF download
  5. Option to download today’s entire cause list
  6. Results saved to JSON file
  7. Simple CLI interface

**UI Features:**

  1. Simple and clean interface (no login needed)
  2. Input either CNR or Case Type + Number + Year
  3. Option to download result JSON
  4. Works in real-time using live eCourts data

**#Install dependencies:**

pip install -r requirements.txt

**# Run The Script:**

Run Streamlit UI- streamlit run ecourts_scraper_app.py

Using CNR number: python ecourts_scraper.py --cnr MHJK010000002023

Using Case Type + Number + Year: python ecourts_scraper.py --case_type CR --case_no 100 --case_year 2023

With Cause List Download: python ecourts_scraper.py --cnr MHJK010000002023 --causelist

**# Output:**

Displays case status in the console.

Saves extracted data to:  case_result.json

If available, saves:

Case PDF → case_<number>.pdf

Cause list → cause_list.pdf

Or use the sample CNR for verification: MHJK010000002023

**Future Improvements:**

  1. Add Flask or Streamlit UI for web interface
  2. Handle captcha-based case search (if required)
  3. Cache results for faster repeated lookups
  4. Add testing flag (--test) for offline demo mode
