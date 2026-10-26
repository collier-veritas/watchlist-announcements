"""Microsoft Graph app-only send (same Entra app as the other AutoEmails projects)."""
import base64
from datetime import datetime
from html import escape
from zoneinfo import ZoneInfo

import requests

from watch.asx import pdf_filename

SYDNEY = ZoneInfo("Australia/Sydney")


def _release_time(a):
    t = datetime.fromisoformat(a.released).astimezone(SYDNEY)
    return f"{t.strftime('%a %d %b')} {t.hour % 12 or 12}:{t:%M}{'am' if t.hour < 12 else 'pm'}"


def build_message(a, pdf, recipients, disclaimer_html):
    body = (
        f'<div style="font-family:Arial,sans-serif;font-size:10pt">'
        f"<p><b>{escape(a.ticker)}</b> &ndash; {escape(a.headline)}<br>"
        f"Released {_release_time(a)} &middot; {escape(a.type.title())} &middot; "
        f"Price sensitive: {'Yes' if a.price_sensitive else 'No'}</p>"
        f"{disclaimer_html}</div>"
    )
    return {
        "subject": f"{a.ticker} - {a.headline}",
        "body": {"contentType": "HTML", "content": body},
        "toRecipients": [{"emailAddress": {"address": r}} for r in recipients],
        "attachments": [{
            "@odata.type": "#microsoft.graph.fileAttachment",
            "name": pdf_filename(a),
            "contentType": "application/pdf",
            "contentBytes": base64.b64encode(pdf).decode(),
        }],
    }


def graph_token(env):
    resp = requests.post(
        f"https://login.microsoftonline.com/{env['GRAPH_TENANT_ID']}/oauth2/v2.0/token",
        data={
            "client_id": env["GRAPH_CLIENT_ID"],
            "client_secret": env["GRAPH_CLIENT_SECRET"],
            "scope": "https://graph.microsoft.com/.default",
            "grant_type": "client_credentials",
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def send(message, sender, token):
    resp = requests.post(
        f"https://graph.microsoft.com/v1.0/users/{sender}/sendMail",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": message, "saveToSentItems": True},
        timeout=60,
    )
    resp.raise_for_status()
