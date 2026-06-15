#!/usr/bin/env python3
"""Record daily sales scoreboard answers to Google Sheet.
Usage:
  python3 record_daily.py --leads 15 --calls 8 --conversations 3 --appointments 1 --followups 5 --proposals 1 --clients 1 --referrals 2 --revenue 500000

To check if today has a row: python3 record_daily.py --check
To record with notes:   python3 record_daily.py ... --notes "Good day"
"""

import json, sys, os, argparse
from datetime import datetime, timezone, timedelta
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SHEET_ID = "1vjrtCmkoQlCV7CdL44ucuh0MbT_UFU2MxBel4km9RnQ"

def get_credentials():
    token_path = os.path.expanduser("~/.hermes/google_token.json")
    alt_paths = ["/opt/data/google_token.json"]
    for p in [token_path] + alt_paths:
        if os.path.exists(p):
            with open(p) as f:
                return Credentials.from_authorized_user_info(json.load(f))
    raise FileNotFoundError("No google_token.json found")

def get_today_row(service):
    tz = timezone(timedelta(hours=8))
    today = datetime.now(tz)
    date_str = today.strftime("%Y-%m-%d")
    result = service.spreadsheets().values().get(
        spreadsheetId=SHEET_ID, range="'Daily Scoreboard'!A:A"
    ).execute()
    for i, row in enumerate(result.get('values', [])):
        if row and row[0] == date_str:
            return i + 1
    return None

def create_today_row(service):
    tz = timezone(timedelta(hours=8))
    today = datetime.now(tz)
    date_str = today.strftime("%Y-%m-%d")
    day_str = today.strftime("%A")
    week_num = today.isocalendar()[1]
    result = service.spreadsheets().values().get(
        spreadsheetId=SHEET_ID, range="'Daily Scoreboard'!A:A"
    ).execute()
    next_row = len(result.get('values', [])) + 1
    service.spreadsheets().values().update(
        spreadsheetId=SHEET_ID,
        range=f"'Daily Scoreboard'!A{next_row}:C{next_row}",
        valueInputOption='RAW',
        body={'values': [[date_str, day_str, f"Week {week_num}"]]}
    ).execute()
    return next_row

def record_answers(leads=0, calls=0, conversations=0, appointments=0, followups=0,
                   proposals=0, clients=0, referrals=0, revenue=0, notes=""):
    creds = get_credentials()
    service = build('sheets', 'v4', credentials=creds)
    row = get_today_row(service) or create_today_row(service)

    targets = [20, 10, 3, 1, 5, 1, 1, 1, 500000]
    values = [leads, calls, conversations, appointments, followups,
              proposals, clients, referrals, revenue]
    score = sum(2 if v >= t else (1 if v > 0 else 0) for v, t in zip(values, targets))
    max_score = 18
    pct = round((score / max_score) * 100)

    data = [*values, f"{score}/{max_score} ({pct}%)", "Answered ✅", notes]
    service.spreadsheets().values().update(
        spreadsheetId=SHEET_ID,
        range=f"'Daily Scoreboard'!D{row}:O{row}",
        valueInputOption='RAW',
        body={'values': [data]}
    ).execute()

    grade = 'A' if pct >= 80 else 'B' if pct >= 65 else 'C' if pct >= 50 else 'D' if pct >= 30 else 'F'
    return {'score': f"{score}/{max_score}", 'percentage': pct, 'grade': grade}

def main():
    parser = argparse.ArgumentParser(description='Record daily sales scoreboard')
    for arg in ['leads', 'calls', 'conversations', 'appointments', 'followups',
                'proposals', 'clients', 'referrals']:
        parser.add_argument(f'--{arg}', type=int, default=0)
    parser.add_argument('--revenue', type=int, default=0)
    parser.add_argument('--notes', type=str, default="")
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()

    if args.check:
        creds = get_credentials()
        service = build('sheets', 'v4', credentials=creds)
        r = get_today_row(service)
        print(f"{'✅' if r else '❌'} Today's row: row {r}" if r else "❌ No row for today")
        return

    result = record_answers(leads=args.leads, calls=args.calls,
        conversations=args.conversations, appointments=args.appointments,
        followups=args.followups, proposals=args.proposals,
        clients=args.clients, referrals=args.referrals,
        revenue=args.revenue, notes=args.notes)
    print(f"Grade: {result['grade']} ({result['percentage']}%) — Score: {result['score']}")

if __name__ == '__main__':
    main()
