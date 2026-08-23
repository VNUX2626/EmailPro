# EmailPro – Assessment 1 Demo

A Flask + SQLite demo web application inspired by the provided assessment tutorial.

## Features
- Dashboard with email/campaign statistics
- CSV email import
- Simple automatic email classification
- Campaign creation
- Demo-mode campaign processing (does not send real emails)
- Campaign reports
- JSON statistics API at `/api/stats`
- Settings page

## Run on Windows
1. Install Python 3.10+.
2. Open this folder in VS Code.
3. Open Terminal and run:
   `python -m venv venv`
4. Activate:
   `venv\Scripts\activate`
5. Install:
   `pip install -r requirements.txt`
6. Start:
   `python app.py`
7. Open:
   `http://127.0.0.1:5000`

## Run on macOS/Linux
`python3 -m venv venv`
`source venv/bin/activate`
`pip install -r requirements.txt`
`python app.py`

## Demo
Use `sample_emails.csv` on the Emails page, then create a campaign.

## Important
This is a portfolio/assessment demo. It does not send real email and does not use real third-party credentials. Add an approved email provider only if the internship instructions explicitly require it.
