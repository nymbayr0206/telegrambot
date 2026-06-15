#!/usr/bin/env python3
"""
Import leads from Google Sheets (Healthcare Leads tab) into Odoo CRM.
Creates "Эрүүл мэндийн байгууллага" tag and assigns to all healthcare leads.

Usage: cd /opt/data && uv run --with google-api-python-client --with google-auth-oauthlib --with google-auth-httplib2 python3 scripts/import_healthcare_leads_to_crm.py

Prerequisites:
- /opt/data/google_token.json (Google OAuth)
- /opt/data/.env (OTO19_* env vars for Odoo)
"""

import json
import os
from xmlrpc.client import ServerProxy

ODOO_URL = os.environ.get('ODOO19_URL', 'http://72.62.197.97:8069')
ODOO_DB = os.environ.get('ODOO19_DB', 'odoo19_admin')
ODOO_USER = os.environ.get('ODOO19_USER', '')
ODOO_PASS = os.environ.get('ODOO19_PASSWORD', '')
COUNTRY_MONGOLIA = 152

if not ODOO_USER or not ODOO_PASS:
    env_file = '/opt/data/.env'
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if '=' in line:
                    k, v = line.split('=', 1)
                    if k == 'ODOO19_USER': ODOO_USER = v
                    elif k == 'ODOO19_PASSWORD': ODOO_PASS = v


def get_sheet_data(sheet_id, sheet_range):
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    creds = Credentials.from_authorized_user_file('/opt/data/google_token.json')
    service = build('sheets', 'v4', credentials=creds)
    data = service.spreadsheets().values().get(
        spreadsheetId=sheet_id, range=sheet_range
    ).execute()
    return data.get('values', [])


def get_odoo():
    common = ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASS, {})
    return uid, ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')


def get_or_create_tag(uid, models, tag_name):
    tag_ids = models.execute_kw(ODOO_DB, uid, ODOO_PASS, 'crm.tag', 'search', [[['name', '=', tag_name]]])
    if tag_ids:
        return tag_ids[0]
    return models.execute_kw(ODOO_DB, uid, ODOO_PASS, 'crm.tag', 'create', [{'name': tag_name, 'color': 2}])


def main():
    SHEET_ID = '1a2GITDSicO6B7WpKmexWZSfM_b5TcZJ5Y7qeLWg95HE'
    TAG_NAME = 'Эрүүл мэндийн байгууллага'

    rows = get_sheet_data(SHEET_ID, 'Healthcare Leads!A1:Z1200')
    leads = rows[1:]  # skip header

    uid, models = get_odoo()
    tag_id = get_or_create_tag(uid, models, TAG_NAME)
    print(f"🏷️ Tag '{TAG_NAME}' (ID: {tag_id})")

    imported, errors = 0, 0
    for i, lead in enumerate(leads):
        if not lead or not lead[2].strip():
            errors += 1
            continue

        phone = lead[15].strip() if lead[15].strip() else lead[16].strip()
        opp_name = lead[2].strip()
        if lead[9].strip():
            opp_name = f"{lead[2].strip()} - {lead[9].strip()[:50]}"

        desc = '\n'.join(f"{k}: {v}" for k, v in [
            ("English Alias", lead[4]), ("Category", lead[1]), ("50+ Employees", lead[5]),
            ("Employee Count", lead[6]), ("Active Jobs", lead[7]), ("Zangia ID", lead[3]),
            ("Source", lead[13]), ("Status", lead[14]), ("HR Phones", lead[15]),
            ("Company Phone", lead[16]), ("Email Source", lead[18]), ("Facebook", lead[19]),
            ("Staff Count", lead[21]), ("Enrichment", lead[22]), ("Zangia Page", lead[10]),
        ] if v.strip())

        vals = {
            'name': opp_name,
            'partner_name': lead[2].strip(),
            'phone': phone,
            'email_from': lead[17].strip(),
            'website': lead[20].strip() or lead[10].strip(),
            'function': lead[9].strip()[:128],
            'street': lead[8].strip(),
            'country_id': COUNTRY_MONGOLIA,
            'tag_ids': [(4, tag_id)],
            'description': desc,
        }

        try:
            models.execute_kw(ODOO_DB, uid, ODOO_PASS, 'crm.lead', 'create', [vals])
            imported += 1
        except Exception as e:
            errors += 1

        if (i + 1) % 25 == 0:
            print(f"  ... {i+1}/{len(leads)} done")

    print(f"\n✅ Imported: {imported}, ❌ Errors: {errors}")


if __name__ == '__main__':
    main()
