#!/usr/bin/env python3
"""
refresh.py — Full pipeline for The Malaysian Lens
==================================================
Runs the full update cycle:
  1. Fetch fresh data from DOSM & BNM APIs
  2. Update index.html with the new data
  3. Push to GitHub + deploy to Vercel via API

Usage:
  python3 refresh.py              # fetch + update + deploy
  python3 refresh.py --no-deploy  # fetch + update only
"""

import subprocess, sys, os, logging, hashlib, json, urllib.request
from datetime import datetime

# Load .env if present (local development)
_env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
if os.path.exists(_env_file):
    for _line in open(_env_file):
        _line = _line.strip()
        if _line and not _line.startswith('#') and '=' in _line:
            _k, _v = _line.split('=', 1)
            os.environ.setdefault(_k.strip(), _v.strip())

# ─── PATHS ───────────────────────────────────────────────────
WEBSITE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR      = os.path.join(WEBSITE_DIR, '..', 'malaysia_economic_db')

# ─── LOGGING ─────────────────────────────────────────────────
log_path = os.path.join(WEBSITE_DIR, 'refresh.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s  %(message)s',
    handlers=[
        logging.FileHandler(log_path),
        logging.StreamHandler(sys.stdout),
    ]
)
log = logging.getLogger(__name__)


def run(cmd, cwd=None, label=''):
    log.info(f"▶ {label or cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.stdout.strip():
        for line in result.stdout.strip().splitlines():
            log.info(f"   {line}")
    if result.returncode != 0:
        log.error(f"   ERROR: {result.stderr.strip()}")
        raise RuntimeError(f"Command failed: {cmd}")
    return result.stdout


# ─── STEP 1: FETCH DATA ──────────────────────────────────────
def step1_fetch_data():
    log.info("─" * 50)
    log.info("STEP 1 — Fetching fresh data from DOSM & BNM")
    log.info("─" * 50)
    try:
        run('python3 main.py', cwd=DB_DIR, label='Fetching DOSM + BNM data')
    except RuntimeError:
        log.warning("   API fetch had errors — continuing with existing CSV data")
        log.warning("   (This is OK if DOSM/BNM APIs are temporarily unavailable)")


# ─── STEP 2: UPDATE CHARTS ───────────────────────────────────
def step2_update_charts():
    log.info("─" * 50)
    log.info("STEP 2 — Updating website charts")
    log.info("─" * 50)
    run('python3 update_data.py', cwd=WEBSITE_DIR, label='Rebuilding chart data')


# ─── VERCEL CONFIG ───────────────────────────────────────────
import os
VERCEL_TOKEN   = os.environ.get('VERCEL_TOKEN',   '')
VERCEL_PROJECT = os.environ.get('VERCEL_PROJECT', 'prj_Yw5kVI99ZedTYAJJzYIAo8LeFJjX')
VERCEL_TEAM    = os.environ.get('VERCEL_TEAM',    'team_exdqjxhX1cxisHdM7Kh28vDZ')

DEPLOY_FILES = [
    'index.html',
    'analysis.html',
    'articles/semiconductors.html',
]


def _sha1(path):
    h = hashlib.sha1()
    with open(path, 'rb') as f:
        h.update(f.read())
    return h.hexdigest()


def _vercel_request(method, endpoint, data=None, raw_body=None, extra_headers=None):
    url = f'https://api.vercel.com{endpoint}'
    headers = {'Authorization': f'Bearer {VERCEL_TOKEN}'}
    if extra_headers:
        headers.update(extra_headers)
    body = None
    if raw_body is not None:
        body = raw_body
    elif data is not None:
        body = json.dumps(data).encode()
        headers['Content-Type'] = 'application/json'
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    ctx = __import__('ssl').create_default_context()
    ctx.load_verify_locations(__import__('certifi').where())
    with urllib.request.urlopen(req, context=ctx) as resp:
        return json.loads(resp.read())


def _vercel_upload(file_path, sha):
    """Upload one file to Vercel's blob store."""
    with open(file_path, 'rb') as f:
        body = f.read()
    _vercel_request(
        'POST', '/v2/files', raw_body=body,
        extra_headers={
            'Content-Type': 'application/octet-stream',
            'x-vercel-digest': sha,
        }
    )


# ─── STEP 3: DEPLOY VIA GIT + VERCEL API ─────────────────────
def step3_deploy():
    log.info("─" * 50)
    log.info("STEP 3 — Pushing to GitHub + deploying to Vercel")
    log.info("─" * 50)

    now_str = datetime.now().strftime('%d %b %Y')

    # 3a — git push (keeps GitHub repo in sync)
    run('git add index.html articles/', cwd=WEBSITE_DIR, label='Staging updated files')
    run(
        f'git -c user.name="The Malaysian Lens" -c user.email="hello@themalaysialens.org" '
        f'commit --allow-empty -m "data: refresh {now_str}"',
        cwd=WEBSITE_DIR,
        label=f'Committing data refresh ({now_str})',
    )
    run('git push origin main', cwd=WEBSITE_DIR, label='Pushing to GitHub')

    # 3b — upload files to Vercel and create a production deployment
    log.info("▶ Uploading files to Vercel")
    file_specs = []
    for rel in DEPLOY_FILES:
        abs_path = os.path.join(WEBSITE_DIR, rel)
        sha = _sha1(abs_path)
        size = os.path.getsize(abs_path)
        _vercel_upload(abs_path, sha)
        log.info(f"   uploaded {rel}")
        file_specs.append({'file': rel, 'sha': sha, 'size': size})

    log.info("▶ Creating Vercel production deployment")
    result = _vercel_request(
        'POST',
        f'/v13/deployments?teamId={VERCEL_TEAM}',
        data={
            'name': 'the-malaysian-lens',
            'files': file_specs,
            'projectSettings': {'framework': None},
            'target': 'production',
        }
    )
    deploy_url = result.get('url', '')
    log.info(f"   ✅ Deployed — https://{deploy_url}")
    log.info("   ✅ Live at https://themalaysialens.org")


# ─── MAIN ────────────────────────────────────────────────────
if __name__ == '__main__':
    no_deploy = '--no-deploy' in sys.argv
    start = datetime.now()

    log.info("=" * 50)
    log.info("  The Malaysian Lens — Daily Refresh")
    log.info(f"  {start.strftime('%d %b %Y %H:%M')}")
    log.info("=" * 50)

    try:
        step1_fetch_data()
        step2_update_charts()

        if not no_deploy:
            step3_deploy()
        else:
            log.info("Deploy skipped (--no-deploy flag)")

        elapsed = (datetime.now() - start).seconds
        log.info(f"\n  Done in {elapsed}s — themalaysialens.org is up to date")

    except Exception as e:
        log.error(f"\n❌ Pipeline failed: {e}")
        sys.exit(1)
