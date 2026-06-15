#!/usr/bin/env python3
"""
Import leads from any Google Sheet tab into Odoo CRM with tagging.

Reads credentials from /opt/data/.env and /opt/data/google_token.json.
"""

import json, os, sys
from xmlrpc.client import ServerProxy

# --- CONFIG ---
COUNTRY_MONGOLIA = 152
MAILING_CONTACT_MODEL_ID = 970

def get_odoocreds():
    url = os.environ.get('ODOO19_URL', 'http://72.62.197.97:8069')
    db = os.environ.get('ODOO19_DB', 'odoo19_admin')
    user = os.environ.get('ODOO19_USER', '')
    pwd = os.environ.get('ODOO19_PASSWORD', '')
    envfile = '/opt/data/.env'
    if os.path.exists(envfile) and (not user or not pwd):
        with open(envfile) as f:
            for line in f:
                line = line.strip()
                if '=' in line:
                    k, v = line.split('=', 1)
                    if k == 'ODOO19_USER': user = v
                    elif k == 'ODOO19_PASSWORD': pwd = v
    return url, db, user, pwd

def get_sheet_data(sheet_id, sheet_range):
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    creds = Credentials.from_authorized_user_file('/opt/data/google_token.json')
    service = build('sheets', 'v4', credentials=creds)
    data = service.spreadsheets().values().get(spreadsheetId=sheet_id, range=sheet_range).execute()
    return data.get('values', [])

def get_or_create_tag(uid, models, db, pwd, name):
    existing = models.execute_kw(db, uid, pwd, 'crm.tag', 'search', [[['name', '=', name]]])
    if existing:
        return existing[0]
    return models.execute_kw(db, uid, pwd, 'crm.tag', 'create', [{'name': name, 'color': 2}])

def create_lead(uid, models, db, pwd, vals):
    return models.execute_kw(db, uid, pwd, 'crm.lead', 'create', [vals])
