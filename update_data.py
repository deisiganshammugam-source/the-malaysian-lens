#!/usr/bin/env python3
"""
update_data.py — The Malaysian Lens data injector
Reads CSVs from malaysia_economic_db and injects the DATA object into index.html
between // DATA_START and // DATA_END markers.
"""

import csv, json, os, re
from datetime import datetime
from collections import defaultdict

DB   = os.path.expanduser('~/Projects/malaysia_economic_db/data')
SITE = os.path.expanduser('~/Projects/my_website')

# ─── helpers ──────────────────────────────────────────────────────────────────

def read_csv(path):
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def sf(v, default=None):
    try:
        f = float(str(v).strip())
        if f != f: return default
        return f
    except (ValueError, TypeError):
        return default

def r2(v):
    x = sf(v)
    return round(x, 2) if x is not None else None

def r1(v):
    x = sf(v)
    return round(x, 1) if x is not None else None

# ─── static mappings ──────────────────────────────────────────────────────────

SECTOR_NAMES = {
    'p1': 'Agriculture', 'p2': 'Mining & Quarrying', 'p3': 'Manufacturing',
    'p4': 'Construction', 'p5': 'Services', 'p6': 'Taxes less Subsidies',
}

COICOP_NAMES = {
    '01': 'Food & Non-Alcoholic Beverages', '02': 'Alcoholic Beverages & Tobacco',
    '03': 'Clothing & Footwear', '04': 'Housing, Water, Electricity & Gas',
    '05': 'Furnishings & Household Equipment', '06': 'Health',
    '07': 'Transport', '08': 'Information & Communication',
    '09': 'Recreation, Sport & Culture', '10': 'Education',
    '11': 'Restaurants & Accommodation', '12': 'Insurance & Financial Services',
    '13': 'Personal Care & Miscellaneous',
}

CPI_WEIGHTS = {
    '01': 29.5, '02': 2.5, '03': 3.3, '04': 23.8, '05': 4.2,
    '06': 1.9, '07': 13.5, '08': 7.0, '09': 4.8, '10': 1.7,
    '11': 3.0, '12': 3.2, '13': 1.6,
}

SITC_NAMES = {
    '0': 'Food & Live Animals', '1': 'Beverages & Tobacco',
    '2': 'Crude Materials', '3': 'Mineral Fuels & Lubricants',
    '4': 'Animal & Vegetable Oils', '5': 'Chemicals',
    '6': 'Manufactured Goods', '7': 'Machinery & Electronics',
    '8': 'Misc. Manufactured Articles', '9': 'Other Commodities',
}

OPR_HISTORY = [
    {'date': '2018-01-25', 'rate': 3.25},
    {'date': '2019-05-07', 'rate': 3.00},
    {'date': '2020-01-22', 'rate': 2.75},
    {'date': '2020-03-03', 'rate': 2.50},
    {'date': '2020-05-05', 'rate': 2.00},
    {'date': '2020-07-07', 'rate': 1.75},
    {'date': '2022-05-11', 'rate': 2.00},
    {'date': '2022-07-06', 'rate': 2.25},
    {'date': '2022-09-08', 'rate': 2.50},
    {'date': '2022-11-03', 'rate': 2.75},
    {'date': '2026-03-05', 'rate': 2.75},
]

# ─── builders ─────────────────────────────────────────────────────────────────

def build_gdp_annual():
    rows   = read_csv(f'{DB}/gdp/gdp_annual.csv')
    growth = {r['date'][:4]: r for r in rows if r['series'] == 'growth_yoy'}
    abs_r  = {r['date'][:4]: r for r in rows if r['series'] == 'abs'}
    result = []
    for yr in sorted(growth.keys()):
        g = growth[yr]
        a = abs_r.get(yr, {})
        gdp_bn = sf(a.get('gdp'))
        result.append({
            'year':      int(yr),
            'growth':    r1(g['gdp']),
            'abs_gdp':   round(gdp_bn / 1000, 1) if gdp_bn else None,
            'gdp_capita': r1(g.get('gdp_capita')),
        })
    return result

def build_gdp_quarterly():
    rows  = read_csv(f'{DB}/gdp/gdp_quarterly.csv')
    qrows = sorted([r for r in rows if r['series'] == 'growth_yoy' and r['date'] >= '2015-01-01'],
                   key=lambda x: x['date'])[-24:]
    return [{'date': r['date'][:7], 'growth': r1(r['value'])} for r in qrows]

def build_gdp_sectors():
    rows = read_csv(f'{DB}/gdp/gdp_by_sector.csv')
    g    = [r for r in rows if r['series'] == 'growth_yoy' and r['sector'] in SECTOR_NAMES]
    latest = max(r['date'] for r in g)
    result = [{'name': SECTOR_NAMES[r['sector']], 'value': r1(r['value'])}
              for r in g if r['date'] == latest]
    return sorted(result, key=lambda x: (x['value'] or 0), reverse=True)

def build_gdp_expenditure():
    rows = read_csv(f'{DB}/gdp/gdp_by_expenditure.csv')
    by_year = defaultdict(lambda: defaultdict(float))
    for r in rows:
        if r['series'] == 'abs':
            by_year[r['date'][:4]][r['type']] += sf(r['value'], 0)
    years, priv, govt, inv, net = [], [], [], [], []
    for yr in sorted(by_year.keys()):
        if int(yr) < 2015: continue
        d = by_year[yr]; gdp = d.get('e0', 1) or 1
        years.append(int(yr))
        priv.append(round(d.get('e1', 0) / gdp * 100, 1))
        govt.append(round(d.get('e2', 0) / gdp * 100, 1))
        inv.append( round(d.get('e3', 0) / gdp * 100, 1))
        net.append( round((d.get('e5', 0) - d.get('e6', 0)) / gdp * 100, 1))
    return {'years': years, 'private_consumption': priv, 'govt_consumption': govt,
            'investment': inv, 'net_exports': net}

def build_inflation_headline():
    rows = read_csv(f'{DB}/inflation/cpi_headline.csv')
    data = sorted([r for r in rows if r['division'] == 'overall' and r.get('inflation_yoy','').strip()],
                  key=lambda x: x['date'])
    return [{'date': r['date'][:7], 'yoy': r1(r['inflation_yoy'])} for r in data]

def build_inflation_core():
    rows = read_csv(f'{DB}/inflation/cpi_core.csv')
    data = sorted([r for r in rows if r['division'] == 'overall' and r.get('inflation_yoy','').strip()],
                  key=lambda x: x['date'])
    return [{'date': r['date'][:7], 'yoy': r1(r['inflation_yoy'])} for r in data]

def build_inflation_components():
    rows   = read_csv(f'{DB}/inflation/cpi_headline.csv')
    divs   = [r for r in rows if r['division'] != 'overall' and r.get('inflation_yoy','').strip()]
    latest = max(r['date'] for r in divs)
    by_div = {r['division']: r for r in divs if r['date'] == latest}
    result = []
    for code, name in COICOP_NAMES.items():
        r = by_div.get(code)
        if not r: continue
        yoy    = r1(r['inflation_yoy'])
        weight = CPI_WEIGHTS.get(code, 0)
        result.append({
            'code': code, 'name': name, 'latest_yoy': yoy,
            'weight': weight, 'contribution': round((weight / 100.0) * (yoy or 0), 3),
        })
    return sorted(result, key=lambda x: (x['latest_yoy'] or 0), reverse=True)

def build_inflation_by_division():
    rows   = read_csv(f'{DB}/inflation/cpi_headline.csv')
    by_div = defaultdict(list)
    for r in rows:
        if r['division'] != 'overall' and r.get('inflation_yoy','').strip():
            by_div[r['division']].append({'date': r['date'][:7], 'yoy': r1(r['inflation_yoy'])})
    return {div: sorted(s, key=lambda x: x['date'])[-48:] for div, s in by_div.items()}

def build_trade_annual():
    rows = read_csv(f'{DB}/trade/trade_by_commodity.csv')
    by_year = defaultdict(lambda: {'e': 0.0, 'i': 0.0})
    for r in rows:
        if r['section'] == 'overall':
            yr = r['date'][:4]
            by_year[yr]['e'] += sf(r['exports'], 0)
            by_year[yr]['i'] += sf(r['imports'], 0)
    import datetime
    cur_year = datetime.date.today().year
    result = []
    for yr in sorted(by_year.keys()):
        if int(yr) < 2015: continue
        if int(yr) >= cur_year: continue  # exclude partial current year
        e = round(by_year[yr]['e'] / 1e9, 1)
        i = round(by_year[yr]['i'] / 1e9, 1)
        result.append({'year': int(yr), 'exports_bn': e, 'imports_bn': i, 'balance_bn': round(e - i, 1)})
    return result

def build_trade_by_commodity():
    rows = read_csv(f'{DB}/trade/trade_by_commodity.csv')
    by_sec = defaultdict(list)
    for r in rows:
        if r['section'] in SITC_NAMES:
            by_sec[r['section']].append({
                'date': r['date'][:7],
                'exports_bn': round(sf(r['exports'], 0) / 1e9, 2),
                'imports_bn': round(sf(r['imports'], 0) / 1e9, 2),
            })
    result = {}
    for sec, series in by_sec.items():
        series.sort(key=lambda x: x['date'])
        latest = series[-1]
        result[sec] = {
            'name': SITC_NAMES[sec],
            'exports_latest_bn': latest['exports_bn'],
            'imports_latest_bn': latest['imports_bn'],
            'trend': series[-36:],
        }
    return result

def build_fx():
    rows = read_csv(f'{DB}/exchange_rates/exchange_rates.csv')
    avgs = sorted([r for r in rows if r['indicator'] == 'avg' and r.get('usd','').strip()
                   and r['date'] >= '2020-01-01'], key=lambda x: x['date'])
    labels = [r['date'][:7] for r in avgs]
    all_avgs = sorted([r for r in rows if r['indicator'] == 'avg' and r.get('usd','').strip()],
                      key=lambda x: x['date'])
    return {
        'labels': labels,
        'usdmyr': [{'date': r['date'][:7], 'rate': r2(sf(r['usd']))} for r in all_avgs[-60:]],
        'multi': {
            'labels': labels,
            'usd': [r2(sf(r['usd'])) for r in avgs],
            'sgd': [r2(sf(r['sgd'])) for r in avgs],
            'cny': [r2(sf(r['cny'])) for r in avgs],
            'eur': [r2(sf(r['eur'])) for r in avgs],
            'jpy': [r2(sf(r['jpy'])) for r in avgs],
        },
    }

def build_opr():
    rows    = read_csv(f'{DB}/interest_rates/opr_historical.csv')
    history = list(OPR_HISTORY)
    if rows:
        r = rows[-1]
        history[-1] = {'date': r['date'], 'rate': sf(r['opr_pct'])}
    history.sort(key=lambda x: x['date'])
    return [{'date': h['date'][:7], 'rate': h['rate']} for h in history]

def build_base_rates():
    rows = read_csv(f'{DB}/interest_rates/base_rates_today.csv')
    result = []
    for r in rows:
        br = sf(r.get('base_rate'))
        if br is None: continue
        result.append({
            'name': r.get('bank_name', r.get('bank_code', '')),
            'br':  r2(br),
            'blr': r2(sf(r.get('base_lending_rate'))),
            'elf': r2(sf(r.get('indicative_eff_lending_rate'))),
        })
    return sorted(result, key=lambda x: x['br'])

def build_money():
    rows = read_csv(f'{DB}/money_supply/money_supply.csv')
    if not rows:
        return {'labels': [], 'm1_growth': [], 'm2_growth': [], 'm3_growth': [], 'snapshot': {}}
    r = rows[0]
    mo = r.get('month_dt','1').zfill(2)
    return {
        'labels': [f"{r.get('year_dt','2026')}-{mo}"],
        'm1_growth': [], 'm2_growth': [], 'm3_growth': [],
        'snapshot': {
            'm1_rm_bn': round(sf(r.get('curr_circ'), 0) / 1000, 1),
            'm3_rm_bn': round(sf(r.get('tot_lia'), 0) / 1000, 1),
        },
    }

# ─── main ─────────────────────────────────────────────────────────────────────

def main():
    print('Building data...')
    gdp_annual      = build_gdp_annual()
    gdp_quarterly   = build_gdp_quarterly()
    gdp_sectors     = build_gdp_sectors()
    gdp_expenditure = build_gdp_expenditure()
    infl_headline   = build_inflation_headline()
    infl_core       = build_inflation_core()
    infl_components = build_inflation_components()
    infl_by_div     = build_inflation_by_division()
    trade_annual    = build_trade_annual()
    trade_commodity = build_trade_by_commodity()
    fx              = build_fx()
    opr             = build_opr()
    base_rates      = build_base_rates()
    money           = build_money()

    # Ticker quick-access values
    ticker = {
        'gdp_growth':    gdp_annual[-1]['growth'] if gdp_annual else None,
        'cpi':           infl_headline[-1]['yoy'] if infl_headline else None,
        'core_cpi':      infl_core[-1]['yoy'] if infl_core else None,
        'opr':           opr[-1]['rate'] if opr else None,
        'usdmyr':        fx['usdmyr'][-1]['rate'] if fx['usdmyr'] else None,
        'trade_balance': trade_annual[-1]['balance_bn'] if trade_annual else None,
        'm3_bn':         money['snapshot'].get('m3_rm_bn'),
    }

    DATA = {
        '_lastUpdated': datetime.now().strftime('%d %B %Y, %H:%M'),
        'ticker': ticker,
        'gdp': {'annual': gdp_annual, 'quarterly': gdp_quarterly,
                'sectors': gdp_sectors, 'expenditure': gdp_expenditure},
        'inflation': {'headline': infl_headline, 'core': infl_core,
                      'components': infl_components, 'by_division': infl_by_div},
        'trade': {'annual': trade_annual, 'by_commodity': trade_commodity},
        'fx': fx,
        'rates': {'opr': opr},
        'baseRates': base_rates,
        'money': money,
    }

    html_path = os.path.join(SITE, 'index.html')
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()

    data_js  = 'const DATA = ' + json.dumps(DATA, indent=2, ensure_ascii=False) + ';'
    new_block = f'// DATA_START\n{data_js}\n// DATA_END'
    new_html, n = re.subn(r'// DATA_START.*?// DATA_END', new_block, html, flags=re.DOTALL)

    if n == 0:
        print('ERROR: DATA_START / DATA_END markers not found in index.html')
        return

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(new_html)

    print(f'  GDP annual: {len(gdp_annual)} years, latest {gdp_annual[-1]["year"]} = {gdp_annual[-1]["growth"]}%')
    print(f'  GDP quarterly: {len(gdp_quarterly)} quarters, latest = {gdp_quarterly[-1]["growth"]}%')
    print(f'  CPI headline: {len(infl_headline)} months, latest = {infl_headline[-1]["yoy"]}%')
    print(f'  CPI core: {len(infl_core)} months, latest = {infl_core[-1]["yoy"]}%')
    print(f'  FX: {len(fx["usdmyr"])} months, latest USD/MYR = {fx["usdmyr"][-1]["rate"]}')
    print(f'  OPR: current = {opr[-1]["rate"]}%')
    print(f'  Base rates: {len(base_rates)} banks')
    print(f'  DATA injected -> index.html  [last updated: {DATA["_lastUpdated"]}]')

if __name__ == '__main__':
    main()
