#!/usr/bin/env python3
"""
Create an Odoo Mass Mailing campaign with an HTML body.

Usage:
  python3 scripts/create_email_campaign.py --name "Campaign" --subject "Subject" --body-html /path/to/email.html --list-id 2

Reads Odoo credentials from /opt/data/.env.
"""

import json, os, sys, argparse
from xmlrpc.client import ServerProxy

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

def read_html(path):
    with open(path) as f:
        full = f.read()
    # Extract only the email body if it has campaign plan below
    start = full.find('<!-- ===== EMAIL PREVIEW ===== -->')
    end = full.find('<!-- ===== CAMPAIGN PLAN ===== -->')
    if start >= 0 and end >= 0:
        return full[start:end]
    return full

def main():
    parser = argparse.ArgumentParser(description='Create Odoo Mass Mailing')
    parser.add_argument('--name', required=True, help='Internal campaign name')
    parser.add_argument('--subject', required=True, help='Email subject line')
    parser.add_argument('--body-html', required=True, help='Path to HTML file')
    parser.add_argument('--list-id', type=int, default=2, help='Mailing list ID (default: 2 = healthcare)')
    parser.add_argument('--email-from', default='AgenticForce <info@agenticforce.mn>', help='Sender email')
    args = parser.parse_args()

    url, db, user, pwd = get_odoocreds()
    body = read_html(args.body_html)

    common = ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, user, pwd, {})
    models = ServerProxy(f'{url}/xmlrpc/2/object')

    mailing_id = models.execute_kw(db, uid, pwd, 'mailing.mailing', 'create', [{
        'name': args.name,
        'subject': args.subject,
        'body_html': body,
        'email_from': args.email_from,
        'contact_list_ids': [(4, args.list_id)],
        'mailing_model_id': 970,
        'mailing_type': 'mail',
        'reply_to_mode': 'new',
        'state': 'draft',
    }])

    print(json.dumps({
        'status': 'created', 'id': mailing_id,
        'name': args.name, 'subject': args.subject,
        'url': f'{url}/web#id={mailing_id}&model=mailing.mailing&view_type=form'
    }, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
