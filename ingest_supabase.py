#!/usr/bin/env python3
"""
ingest_supabase.py — Push economic data to Supabase
Reads CSVs via update_data.build_data(), upserts to dashboard_data table.

Usage:
  python3 ingest_supabase.py
"""

import os, json, sys, urllib.request, ssl

# Load .env
_env = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
if os.path.exists(_env):
    for _line in open(_env):
        _line = _line.strip()
        if _line and not _line.startswith('#') and '=' in _line:
            _k, _v = _line.split('=', 1)
            os.environ.setdefault(_k.strip(), _v.strip())

SUPABASE_URL     = os.environ.get('SUPABASE_URL', '')
SERVICE_KEY      = os.environ.get('SUPABASE_SERVICE_KEY', '')

if not SUPABASE_URL or not SERVICE_KEY:
    print('ERROR: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env')
    sys.exit(1)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from update_data import build_data

def _ssl_ctx():
    ctx = ssl.create_default_context()
    for cert in ('/etc/ssl/cert.pem', '/etc/ssl/certs/ca-certificates.crt'):
        if os.path.exists(cert):
            ctx.load_verify_locations(cert)
            break
    return ctx

def ingest():
    print('Building data from CSVs...')
    data = build_data()

    payload = json.dumps({
        'id': 1,
        'data': data,
    }).encode()

    req = urllib.request.Request(
        f'{SUPABASE_URL}/rest/v1/dashboard_data',
        data=payload,
        headers={
            'apikey':        SERVICE_KEY,
            'Authorization': f'Bearer {SERVICE_KEY}',
            'Content-Type':  'application/json',
            'Prefer':        'resolution=merge-duplicates',
        },
        method='POST'
    )

    try:
        with urllib.request.urlopen(req, context=_ssl_ctx()) as resp:
            print(f'Supabase: {resp.status} — upload OK')
    except urllib.error.HTTPError as e:
        print(f'Supabase error {e.code}: {e.read().decode()[:300]}')
        sys.exit(1)

    print(f'  GDP:  {data["gdp"]["annual"][-1]["year"]} = {data["gdp"]["annual"][-1]["growth"]}%')
    print(f'  CPI:  {data["inflation"]["headline"][-1]["yoy"]}%  (core {data["inflation"]["core"][-1]["yoy"]}%)')
    print(f'  OPR:  {data["rates"]["opr"][-1]["rate"]}%')
    print(f'  FX:   USD/MYR {data["fx"]["usdmyr"][-1]["rate"]}')
    print(f'  Updated: {data["_lastUpdated"]}')

if __name__ == '__main__':
    ingest()
