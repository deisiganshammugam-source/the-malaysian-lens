"""
new_post.py — The Malaysian Lens Post Generator
================================================
Claude uses this script to add new articles to the website.

Usage:
  python3 new_post.py

Just fill in the POST_DATA dict at the top and run.
The script will:
  1. Generate the article HTML file in /articles/
  2. Add the article card to the homepage (index.html)
"""

import os, json, sys, urllib.request, ssl

# ─────────────────────────────────────────────
# FILL THIS IN FOR EACH NEW POST
# ─────────────────────────────────────────────
POST_DATA = {
    "slug":       "malaysia-2025-economic-developments",
    "title":      "Malaysia 2025: Economic Developments",
    "subtitle":   "Growth accelerated to 5.2 percent for the full year, surging to 6.3 percent in Q4 on the back of a powerful domestic investment cycle. Core inflation is rising and external risks are building.",
    "category":   "Macroeconomic Review",
    "tags":       ["GDP", "CPI", "BNM", "DOSM"],
    "date":       "March 2026",
    "emoji":      "📈",
    "excerpt":    "Malaysia's economy expanded 5.2 percent in 2025, accelerating to 6.3 percent in Q4 — the fastest quarterly outturn in two years. Growth was driven by a self-reinforcing investment cycle, solid private consumption, and recovering exports. But core inflation is drifting upward and external headwinds are building.",
    "body_html":  """
        <div class="key-numbers">
          <div class="key-num"><div class="val">5.2%</div><div class="lbl">GDP Growth 2025 (Full Year)</div></div>
          <div class="key-num"><div class="val">RM 154.6b</div><div class="lbl">Trade Surplus 2025</div></div>
          <div class="key-num"><div class="val">2.3%</div><div class="lbl">Core CPI (Dec 2025)</div></div>
        </div>

        <h2>Growth Performance</h2>
        <p><strong>Malaysia's economy delivered its strongest performance since the post-pandemic rebound, expanding 5.2 percent in 2025 and accelerating sharply through the year to register the fastest quarterly growth rate in more than two years.</strong> After a subdued first half — output grew 4.4 percent in both Q1 and Q2 — momentum gathered decisively: GDP expanded 5.4 percent in Q3 and 6.3 percent in Q4 on a year-on-year basis, the latter also gaining 3.3 percent on a sequential basis. The sequential pickup in Q4 confirms that the acceleration reflected genuine underlying demand rather than base effects alone. On a full-year basis, 2025 marked Malaysia's strongest outturn since 2022, driven by a broad-based expansion across services, manufacturing, and construction, and exceeded most official forecasts heading into the year.</p>

        <div class="data-table-wrapper">
          <div class="data-table-title">Quarterly GDP Growth, 2025 (Year-on-Year, %)</div>
          <table>
            <thead><tr><th>Quarter</th><th>YoY Growth</th><th>QoQ Growth</th></tr></thead>
            <tbody>
              <tr><td>Q1 2025</td><td>4.4%</td><td>&ndash;3.5%</td></tr>
              <tr><td>Q2 2025</td><td>4.4%</td><td>1.0%</td></tr>
              <tr><td>Q3 2025</td><td>5.4%</td><td>5.7%</td></tr>
              <tr><td>Q4 2025</td><td>6.3%</td><td>3.3%</td></tr>
            </tbody>
          </table>
          <div class="table-source">Source: Department of Statistics Malaysia (DOSM) &mdash; February 2026</div>
        </div>

        <div class="chart-container">
          <div class="chart-title">GDP Growth by Sector, Q4 2025 (Year-on-Year, %)</div>
          <canvas id="chartSectorGDP"></canvas>
          <div class="chart-source">Source: DOSM &mdash; February 2026</div>
        </div>

        <div class="section-break">&middot; &middot; &middot;</div>

        <h2>Domestic Demand</h2>
        <p><strong>Domestic demand was the primary engine of growth, with private investment delivering the strongest impulse across all demand components.</strong> Gross fixed capital formation (GFCF) expanded 9.3 percent year-on-year in Q4 &mdash; extending a sustained run of strong investment growth throughout the year &mdash; as capital spending accelerated in semiconductor fabrication, data center infrastructure, and logistics facilities tied to the New Industrial Master Plan 2030. Construction output grew 11.0 percent in Q4, reflecting this physical build-out in the real economy. Private consumption held firm at 5.3 percent in Q4, underpinned by continued employment gains and real wage growth at a time when headline inflation remained contained. Government consumption also contributed, rising 8.0 percent year-on-year in Q4, partly reflecting the full-year impact of the 2024 civil service salary revision and sustained social expenditure. Taken together, these components suggest that domestic demand had become self-reinforcing by the second half of 2025: the investment cycle fed into employment and income growth, which in turn supported consumption &mdash; a virtuous dynamic not always visible in the aggregate growth figure.</p>

        <div class="pull-quote"><p>&ldquo;By Q4 2025, gross fixed capital formation had expanded 9.3 percent &mdash; the physical build-out of Malaysia&rsquo;s technology and industrial ambitions now measurable in the national accounts.&rdquo;</p></div>

        <div class="chart-container">
          <div class="chart-title">Domestic Demand Components, 2025 (Year-on-Year Growth, %)</div>
          <canvas id="chartDomesticDemand"></canvas>
          <div class="chart-source">Source: DOSM &mdash; February 2026</div>
        </div>

        <h2>External Sector</h2>
        <p><strong>The external sector contributed positively but provided a more moderate impulse than domestic demand, with import growth outpacing export growth in Q4.</strong> Exports of goods and services grew 3.9 percent year-on-year in Q4, recovering from a softer 1.7 percent in Q3, as global semiconductor demand improved and commodity exports stabilized. In value terms, total merchandise exports reached approximately RM 1.61 trillion in 2025, generating a trade surplus of around RM 154.6 billion &mdash; a solid buffer that supported the current account position. However, strong investment activity drove capital goods imports sharply higher (+7.9 percent year-on-year in Q4), narrowing the net trade contribution to GDP. The ringgit appreciated meaningfully in the second half of 2025, moving from an average of 4.23 per US dollar in August to 4.09 in December and 4.03 by January 2026, reflecting improved global risk sentiment and capital inflows into regional emerging markets. Currency appreciation, while supportive of import-cost stability, creates a modest competitiveness headwind for export-oriented sectors that warrants monitoring.</p>

        <div class="chart-container">
          <div class="chart-title">External Trade: Exports and Imports Growth, 2025 (Year-on-Year, %)</div>
          <canvas id="chartExternalTrade"></canvas>
          <div class="chart-source">Source: DOSM &mdash; February 2026</div>
        </div>

        <div class="section-break">&middot; &middot; &middot;</div>

        <h2>Inflation</h2>
        <p><strong>Inflation remained well-contained throughout 2025, though an upward drift in core price pressures toward year-end warrants attention.</strong> Headline CPI averaged approximately 1.4 percent for the full year, easing from 1.7 percent in January to a trough of 1.1 percent in June before gradually recovering to 1.6 percent by December &mdash; a level that held into January 2026. This moderation largely reflected favorable food price trends, subdued global commodity prices, and the base effects of prior fuel subsidy adjustments. Core inflation, however, rose steadily from 1.8 percent in January to 2.3 percent by December 2025, a trajectory that continued into January 2026. The widening gap between headline and core readings suggests that underlying demand-side pressures are building &mdash; particularly in services prices &mdash; even as administered price changes have masked their full extent. This divergence merits close monitoring as subsidy rationalization continues through 2026; the headline rate will likely track upward as fuel subsidy targeting proceeds, potentially compressing real household incomes for lower-income groups.</p>

        <div class="data-table-wrapper">
          <div class="data-table-title">CPI Inflation: Headline vs. Core, 2025 (YoY, %)</div>
          <table>
            <thead><tr><th>Month</th><th>Headline CPI</th><th>Core CPI</th></tr></thead>
            <tbody>
              <tr><td>January 2025</td><td>1.7%</td><td>1.8%</td></tr>
              <tr><td>March 2025</td><td>1.4%</td><td>1.9%</td></tr>
              <tr><td>June 2025</td><td>1.1%</td><td>1.8%</td></tr>
              <tr><td>September 2025</td><td>1.5%</td><td>2.1%</td></tr>
              <tr><td>December 2025</td><td>1.6%</td><td>2.3%</td></tr>
              <tr><td>January 2026</td><td>1.6%</td><td>2.3%</td></tr>
            </tbody>
          </table>
          <div class="table-source">Source: Department of Statistics Malaysia (DOSM) &mdash; February 2026</div>
        </div>

        <div class="chart-container">
          <div class="chart-title">Headline vs. Core CPI Inflation, 2025 (Year-on-Year, %)</div>
          <canvas id="chartInflation"></canvas>
          <div class="chart-source">Source: DOSM &mdash; February 2026. Core CPI excludes volatile items (fresh food and administered prices).</div>
        </div>

        <h2>Labour Market</h2>
        <p><strong>Labour market conditions tightened further in 2025, with broad-based employment gains supporting private consumption across income groups.</strong> The unemployment rate remained close to structural lows through the year, while labour force participation continued its gradual upward trend. Employment growth was concentrated in services &mdash; particularly information and communication technology, professional services, and hospitality &mdash; consistent with the sectoral composition of GDP expansion. Nominal wage growth broadly outpaced headline inflation for much of 2025, protecting household real incomes and sustaining consumption momentum among B40 and M40 households. Underemployment nonetheless remained a more nuanced challenge: structural skill mismatches between available labour supply and demand from the rapidly expanding technology and high-value manufacturing sectors continued to limit productivity gains and keep a portion of the labour force in lower-wage roles than their qualifications would otherwise command.</p>

        <div class="chart-container">
          <div class="chart-title">Unemployment Rate and Labour Force Participation, 2025 (Monthly, %)</div>
          <canvas id="chartLabour"></canvas>
          <div class="chart-source">Source: DOSM &mdash; February 2026. LFPR = Labour Force Participation Rate (ages 15&ndash;64).</div>
        </div>

        <div class="section-break">&middot; &middot; &middot;</div>

        <h2>Financial Conditions</h2>
        <p><strong>Financial conditions remained accommodative throughout 2025, with Bank Negara Malaysia holding the Overnight Policy Rate steady at 2.75 percent.</strong> The MPC&rsquo;s decision to maintain rates reflected a balanced assessment: growth was on a solid trajectory, headline inflation was contained, and the external environment &mdash; while uncertain &mdash; did not warrant preemptive policy adjustment. With core inflation stabilizing around 2.0&ndash;2.3 percent by year-end, the real policy rate edged into marginally positive territory, suggesting that the current monetary stance is broadly neutral rather than accommodative in real terms. Credit growth remained supportive of private investment, and banking system buffers were adequate. The appreciating ringgit provided an additional disinflationary channel that gave BNM room to maintain a patient stance without concern about imported price pressures. Looking into 2026, any policy adjustment is more likely to be guided by the durability of the growth acceleration and the trajectory of core inflation than by external rate movements alone.</p>

        <div class="chart-container">
          <div class="chart-title">Overnight Policy Rate (OPR), 2020&ndash;2025 (%)</div>
          <canvas id="chartOPR"></canvas>
          <div class="chart-source">Source: Bank Negara Malaysia (BNM) &mdash; February 2026</div>
        </div>

        <h2>Risks and Outlook</h2>
        <p><strong>The near-term outlook is favorable, but Malaysia&rsquo;s 2026 growth trajectory faces a set of meaningful downside risks that could test the resilience of the domestic demand recovery.</strong> The most significant external risk is a sharper-than-expected slowdown in global trade: escalating US tariff actions on major trading partners &mdash; including China &mdash; could reduce demand for Malaysia&rsquo;s electronics and manufacturing exports more materially than current forecasts assume. A deceleration in China&rsquo;s economy poses an additional direct risk given close bilateral trade and investment linkages, particularly in commodities and intermediate goods. On the domestic side, the pace of subsidy rationalization &mdash; including the planned targeting of RON95 fuel subsidies &mdash; carries a dual risk: while necessary for fiscal consolidation, a poorly sequenced implementation could simultaneously compress household purchasing power and push headline inflation into territory that complicates the monetary policy stance. On the upside, sustained foreign direct investment inflows linked to semiconductor supply chain diversification and data center buildout could extend the investment cycle well into 2026. If global conditions remain broadly benign and investment momentum holds, full-year GDP growth in 2026 is likely to remain in the 4.5&ndash;5.5 percent range &mdash; consistent with Malaysia&rsquo;s medium-term potential output trajectory.</p>

        <p class="disclaimer">Data sourced from the Department of Statistics Malaysia (DOSM) and Bank Negara Malaysia (BNM). All growth rates are year-on-year unless otherwise stated. Trade values are in ringgit; exchange rates are monthly averages.</p>

        <div style="background:#fffbeb;border:1px solid #f3d87a;border-radius:8px;padding:1rem 1.25rem;margin-top:1.5rem;font-size:.82rem;color:#92400e;line-height:1.6;">
          <strong style="color:#78350f;">Disclaimer:</strong> This article, including all text, data tables, and charts, was entirely generated by artificial intelligence (Claude, Anthropic). While data is sourced from official publications by DOSM and BNM, the analysis, interpretation, and presentation may contain errors. This content is for informational purposes only and does not constitute financial advice. The Malaysian Lens accepts no liability for decisions made using this information.
        </div>

        <script>
        (function(){
          var navy='#1a2b4a',gold='#c9a84c',red='#dc2626',teal='#2d8a7e',blue='#2563eb',orange='#ea580c',gridC='#e4e9f0';
          Chart.defaults.font.family="'Inter',sans-serif";Chart.defaults.font.size=12;Chart.defaults.color='#64748b';
          Chart.defaults.plugins.legend.labels.usePointStyle=true;Chart.defaults.plugins.legend.labels.padding=16;

          new Chart(document.getElementById('chartSectorGDP'),{type:'bar',data:{labels:['Construction','Services','Manufacturing','Mining & Quarrying','Agriculture'],datasets:[{label:'Q4 2025 YoY Growth (%)',data:[11.0,6.2,6.1,3.2,2.8],backgroundColor:[gold,navy,teal,blue,orange],borderWidth:0,borderRadius:4,barThickness:28}]},options:{indexAxis:'y',responsive:true,maintainAspectRatio:true,plugins:{legend:{display:false},tooltip:{callbacks:{label:function(c){return c.raw+'%'}}}},scales:{x:{grid:{color:gridC},ticks:{callback:function(v){return v+'%'}},beginAtZero:true},y:{grid:{display:false}}}}});

          new Chart(document.getElementById('chartDomesticDemand'),{type:'bar',data:{labels:['Q1 2025','Q2 2025','Q3 2025','Q4 2025'],datasets:[{label:'Private Consumption',data:[4.8,4.9,5.0,5.3],backgroundColor:navy,borderRadius:3,barPercentage:0.7},{label:'Gross Fixed Capital Formation',data:[6.3,7.1,8.5,9.3],backgroundColor:gold,borderRadius:3,barPercentage:0.7},{label:'Government Consumption',data:[5.5,6.2,7.0,8.0],backgroundColor:teal,borderRadius:3,barPercentage:0.7}]},options:{responsive:true,maintainAspectRatio:true,plugins:{legend:{position:'bottom'},tooltip:{callbacks:{label:function(c){return c.dataset.label+': '+c.raw+'%'}}}},scales:{x:{grid:{display:false}},y:{grid:{color:gridC},ticks:{callback:function(v){return v+'%'}},beginAtZero:true}}}});

          new Chart(document.getElementById('chartExternalTrade'),{type:'bar',data:{labels:['Q1 2025','Q2 2025','Q3 2025','Q4 2025'],datasets:[{label:'Exports',data:[5.1,4.3,1.7,3.9],backgroundColor:navy,borderRadius:3,barPercentage:0.65},{label:'Imports',data:[3.8,5.6,4.2,7.9],backgroundColor:gold,borderRadius:3,barPercentage:0.65}]},options:{responsive:true,maintainAspectRatio:true,plugins:{legend:{position:'bottom'},tooltip:{callbacks:{label:function(c){return c.dataset.label+': '+c.raw+'%'}}}},scales:{x:{grid:{display:false}},y:{grid:{color:gridC},ticks:{callback:function(v){return v+'%'}},title:{display:true,text:'YoY Growth (%)'}}}}});

          new Chart(document.getElementById('chartInflation'),{type:'line',data:{labels:['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec','Jan 26'],datasets:[{label:'Headline CPI',data:[1.7,1.5,1.4,1.3,1.2,1.1,1.2,1.3,1.5,1.5,1.5,1.6,1.6],borderColor:navy,backgroundColor:navy+'18',borderWidth:2.5,pointRadius:3,pointHoverRadius:5,tension:0.3,fill:true},{label:'Core CPI',data:[1.8,1.8,1.9,1.9,1.8,1.8,1.9,2.0,2.1,2.1,2.2,2.3,2.3],borderColor:red,backgroundColor:red+'12',borderWidth:2.5,pointRadius:3,pointHoverRadius:5,tension:0.3,fill:true,borderDash:[6,3]}]},options:{responsive:true,maintainAspectRatio:true,plugins:{legend:{position:'bottom'},tooltip:{callbacks:{label:function(c){return c.dataset.label+': '+c.raw+'%'}}}},scales:{x:{grid:{display:false}},y:{grid:{color:gridC},ticks:{callback:function(v){return v+'%'}},min:0.5,max:3.0,title:{display:true,text:'YoY (%)'}}}}});

          new Chart(document.getElementById('chartLabour'),{type:'line',data:{labels:['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],datasets:[{label:'Unemployment Rate (%)',data:[3.3,3.3,3.2,3.2,3.1,3.1,3.1,3.0,3.0,3.0,3.0,2.9],borderColor:navy,backgroundColor:navy+'15',borderWidth:2.5,pointRadius:3,pointHoverRadius:5,tension:0.3,fill:true,yAxisID:'y'},{label:'LFPR (%)',data:[70.2,70.3,70.3,70.4,70.5,70.5,70.6,70.6,70.7,70.7,70.8,70.9],borderColor:gold,backgroundColor:gold+'15',borderWidth:2.5,pointRadius:3,pointHoverRadius:5,tension:0.3,fill:true,yAxisID:'y1'}]},options:{responsive:true,maintainAspectRatio:true,plugins:{legend:{position:'bottom'},tooltip:{callbacks:{label:function(c){return c.dataset.label+' '+c.raw+'%'}}}},scales:{x:{grid:{display:false}},y:{type:'linear',position:'left',grid:{color:gridC},ticks:{callback:function(v){return v+'%'}},min:2.5,max:3.8,title:{display:true,text:'Unemployment (%)'}},y1:{type:'linear',position:'right',grid:{drawOnChartArea:false},ticks:{callback:function(v){return v+'%'}},min:69.5,max:71.5,title:{display:true,text:'LFPR (%)'}}}}});

          new Chart(document.getElementById('chartOPR'),{type:'line',data:{labels:['Jan 20','May 20','Jul 20','Jan 22','May 22','Jul 22','Sep 22','Nov 22','May 23','Jan 24','Jul 24','Jan 25','Jul 25','Dec 25'],datasets:[{label:'OPR (%)',data:[3.00,2.50,1.75,1.75,2.00,2.25,2.50,2.75,3.00,3.00,3.00,2.75,2.75,2.75],borderColor:navy,backgroundColor:navy+'15',borderWidth:2.5,pointRadius:4,pointHoverRadius:6,pointBackgroundColor:function(ctx){var v=ctx.raw;var p=ctx.dataIndex>0?ctx.dataset.data[ctx.dataIndex-1]:v;return v>p?'#16a34a':v<p?red:navy},stepped:'before',fill:true}]},options:{responsive:true,maintainAspectRatio:true,plugins:{legend:{display:false},tooltip:{callbacks:{label:function(c){return 'OPR: '+c.raw+'%'}}}},scales:{x:{grid:{display:false}},y:{grid:{color:gridC},ticks:{callback:function(v){return v.toFixed(2)+'%'}},min:1.5,max:3.25,title:{display:true,text:'Policy Rate (%)'}}}}});
        })();
        </script>
    """,
    "sources": "Data: DOSM · BNM · World Bank",
}
# ─────────────────────────────────────────────

# Load .env
_env = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
if os.path.exists(_env):
    for _line in open(_env):
        _line = _line.strip()
        if _line and not _line.startswith('#') and '=' in _line:
            _k, _v = _line.split('=', 1)
            os.environ.setdefault(_k.strip(), _v.strip())


def _ssl_ctx():
    ctx = ssl.create_default_context()
    for cert in ('/etc/ssl/cert.pem', '/etc/ssl/certs/ca-certificates.crt'):
        if os.path.exists(cert):
            ctx.load_verify_locations(cert)
            break
    return ctx


def publish(post):
    url = os.environ.get('SUPABASE_URL', '')
    key = os.environ.get('SUPABASE_SERVICE_KEY', '')
    if not url or not key:
        print('ERROR: SUPABASE_URL and SUPABASE_SERVICE_KEY must be in .env')
        sys.exit(1)
    payload = json.dumps({
        'slug':       post['slug'],
        'title':      post['title'],
        'subtitle':   post.get('subtitle', ''),
        'category':   post.get('category', ''),
        'tags':       post.get('tags', []),
        'date_label': post.get('date_label', post.get('date', '')),
        'emoji':      post.get('emoji', ''),
        'excerpt':    post.get('excerpt', ''),
        'body_html':  post.get('body_html', ''),
        'sources':    post.get('sources', ''),
    }).encode()
    req = urllib.request.Request(
        f'{url}/rest/v1/articles',
        data=payload,
        headers={
            'apikey':        key,
            'Authorization': f'Bearer {key}',
            'Content-Type':  'application/json',
            'Prefer':        'resolution=merge-duplicates',
        },
        method='POST'
    )
    try:
        with urllib.request.urlopen(req, context=_ssl_ctx()) as resp:
            print(f'  Supabase: {resp.status} — article upserted')
    except urllib.error.HTTPError as e:
        print(f'  Supabase error {e.code}: {e.read().decode()[:300]}')
        sys.exit(1)


if __name__ == '__main__':
    print(f"\nPublishing: {POST_DATA['title']}")
    print(f"  Slug: {POST_DATA['slug']}\n")
    publish(POST_DATA)
    print(f"\nDone. Article live at: themalaysialens.org/article.html?slug={POST_DATA['slug']}\n")


# ── DEAD CODE BELOW — kept only as reference, no longer used ──────────────────
ARTICLE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{title} — The Malaysian Lens</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {{--navy:#0a1628;--gold:#c9a84c;--cream:#faf8f3;--text:#1a1a2e;--muted:#6b7280;--border:#e5e0d5;--red:#c0392b;}}
    *{{margin:0;padding:0;box-sizing:border-box;}}
    body{{font-family:'Inter',sans-serif;background:var(--cream);color:var(--text);line-height:1.6;}}
    header{{background:var(--navy);border-bottom:3px solid var(--gold);padding:0 2rem;}}
    .header-top{{display:flex;align-items:center;justify-content:space-between;padding:1.5rem 0 1rem;max-width:1100px;margin:0 auto;}}
    .site-name{{font-family:'Playfair Display',serif;font-size:1.8rem;font-weight:900;color:#fff;text-decoration:none;display:block;}}
    .site-name span{{color:var(--gold);}}
    .site-tagline{{font-size:0.7rem;color:#a0aec0;letter-spacing:2px;text-transform:uppercase;margin-top:2px;}}
    nav{{max-width:1100px;margin:0 auto;padding:0.75rem 0;display:flex;gap:2rem;border-top:1px solid rgba(255,255,255,0.1);}}
    nav a{{color:#cbd5e0;text-decoration:none;font-size:0.8rem;letter-spacing:1.5px;text-transform:uppercase;font-weight:500;}}
    nav a:hover{{color:var(--gold);}}
    .date-bar{{background:var(--gold);text-align:center;padding:0.35rem;font-size:0.72rem;letter-spacing:1.5px;text-transform:uppercase;font-weight:600;color:var(--navy);}}
    .article-wrapper{{max-width:720px;margin:3rem auto;padding:0 2rem;}}
    .back-link{{display:inline-flex;align-items:center;gap:0.4rem;font-size:0.78rem;color:var(--muted);text-decoration:none;letter-spacing:1px;text-transform:uppercase;margin-bottom:2rem;}}
    .back-link:hover{{color:var(--gold);}}
    .article-category{{display:inline-block;font-size:0.68rem;letter-spacing:2px;text-transform:uppercase;font-weight:600;color:var(--red);margin-bottom:1rem;}}
    .article-headline{{font-family:'Playfair Display',serif;font-size:2.8rem;font-weight:900;line-height:1.15;color:var(--navy);margin-bottom:1.25rem;}}
    .article-sub{{font-size:1.15rem;color:var(--muted);line-height:1.7;margin-bottom:1.5rem;font-weight:300;border-left:3px solid var(--gold);padding-left:1rem;}}
    .article-meta-bar{{display:flex;align-items:center;gap:1.5rem;padding:1rem 0;border-top:1px solid var(--border);border-bottom:1px solid var(--border);margin-bottom:2rem;font-size:0.8rem;color:var(--muted);flex-wrap:wrap;}}
    .tag{{background:var(--navy);color:var(--gold);padding:0.2rem 0.6rem;border-radius:2px;font-size:0.68rem;letter-spacing:1px;text-transform:uppercase;}}
    .article-body{{font-size:1.05rem;line-height:1.85;}}
    .article-body p{{margin-bottom:1.4rem;}}
    .hook{{font-family:'Playfair Display',serif;font-size:1.4rem;font-weight:700;color:var(--navy);line-height:1.4;margin-bottom:0.5rem;}}
    .hook-sub{{font-size:1rem;color:var(--muted);font-style:italic;margin-bottom:2rem;}}
    .section-break{{text-align:center;color:var(--gold);font-size:1.2rem;letter-spacing:8px;margin:2rem 0;}}
    .data-table-wrapper{{margin:2rem 0;overflow-x:auto;}}
    .data-table-title{{font-size:0.72rem;letter-spacing:2px;text-transform:uppercase;font-weight:600;color:var(--gold);margin-bottom:0.75rem;}}
    table{{width:100%;border-collapse:collapse;font-size:0.88rem;}}
    thead{{background:var(--navy);color:#fff;}}
    thead th{{padding:0.75rem 1rem;text-align:left;font-weight:500;font-size:0.78rem;}}
    tbody tr:nth-child(even){{background:#fff;}}
    tbody tr:nth-child(odd){{background:#f5f2ec;}}
    tbody td{{padding:0.65rem 1rem;border-bottom:1px solid var(--border);}}
    .table-source{{font-size:0.72rem;color:var(--muted);margin-top:0.5rem;font-style:italic;}}
    .pull-quote{{background:var(--navy);color:#fff;padding:2rem;margin:2rem 0;border-left:4px solid var(--gold);}}
    .pull-quote p{{font-family:'Playfair Display',serif;font-size:1.3rem;line-height:1.5;margin-bottom:0;}}
    .key-numbers{{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin:2rem 0;}}
    .key-num{{background:#fff;border:1px solid var(--border);border-top:3px solid var(--gold);padding:1.25rem;text-align:center;}}
    .key-num .val{{font-family:'Playfair Display',serif;font-size:2rem;font-weight:700;color:var(--navy);}}
    .key-num .lbl{{font-size:0.72rem;color:var(--muted);text-transform:uppercase;letter-spacing:1px;margin-top:0.25rem;}}
    .callout{{background:#fff3cd;border-left:4px solid #f59e0b;padding:1.25rem 1.5rem;margin:2rem 0;font-size:0.95rem;}}
    .vigilance-box{{background:var(--navy);color:#e2e8f0;padding:2rem;margin:2.5rem 0 1rem;text-align:center;}}
    .vigilance-box p{{font-family:'Playfair Display',serif;font-size:1.2rem;line-height:1.6;margin-bottom:0;}}
    .vigilance-box .flag{{font-size:1.5rem;margin-top:0.75rem;display:block;}}
    .disclaimer{{font-size:0.78rem;color:var(--muted);font-style:italic;margin-top:1.5rem;padding-top:1.5rem;border-top:1px solid var(--border);}}
    footer{{background:var(--navy);color:#a0aec0;padding:2.5rem 2rem;text-align:center;margin-top:4rem;}}
    footer .footer-name{{font-family:'Playfair Display',serif;font-size:1.3rem;color:var(--gold);margin-bottom:0.5rem;}}
    footer p{{font-size:0.8rem;line-height:1.8;}}
    footer .sources{{margin-top:1rem;font-size:0.72rem;color:#4a5568;}}
    @media(max-width:600px){{.article-headline{{font-size:2rem;}}.key-numbers{{grid-template-columns:1fr;}}}}
  </style>
</head>
<body>
  <header>
    <div class="header-top">
      <div>
        <a href="../index.html" class="site-name">The <span>Malaysian</span> Lens</a>
        <div class="site-tagline">Economic Analysis · Data-Driven · Independent</div>
      </div>
      <div style="font-size:2rem;">🇲🇾</div>
    </div>
    <nav>
      <a href="../index.html">Home</a>
      <a href="../index.html#analysis">Analysis</a>
      <a href="../index.html#data">Key Data</a>
      <a href="../index.html#about">About</a>
    </nav>
  </header>
  <div class="date-bar" id="datebar">Loading...</div>
  <div class="article-wrapper">
    <a href="../index.html" class="back-link">← Back to all analysis</a>
    <span class="article-category">{category}</span>
    <h1 class="article-headline">{title}</h1>
    <p class="article-sub">{subtitle}</p>
    <div class="article-meta-bar">
      {tag_html}
      <span>By Deisigan &nbsp;·&nbsp; {date}</span>
    </div>
    <div class="article-body">
      {body_html}
    </div>
  </div>
  <footer>
    <div class="footer-name">The Malaysian Lens</div>
    <p>Economic Analysis by Deisigan &nbsp;·&nbsp; World Bank Economist &nbsp;·&nbsp; 🇲🇾</p>
    <p class="sources">{sources}</p>
  </footer>
  <script>
    const d = new Date();
    document.getElementById('datebar').textContent =
      d.toLocaleDateString('en-MY', {{weekday:'long',year:'numeric',month:'long',day:'numeric'}}).toUpperCase();
  </script>
</body>
</html>"""


def make_article(post):
    tag_html = " ".join(f'<span class="tag">{t}</span>' for t in post["tags"])
    html = ARTICLE_TEMPLATE.format(
        title=post["title"],
        subtitle=post["subtitle"],
        category=post["category"],
        tags=post["tags"],
        tag_html=tag_html,
        date=post["date"],
        body_html=post["body_html"],
        sources=post["sources"],
    )
    out_path = os.path.join(os.path.dirname(__file__), "articles", f"{post['slug']}.html")
    with open(out_path, "w") as f:
        f.write(html)
    print(f"✅ Article created: articles/{post['slug']}.html")
    return out_path


def add_to_index(post):
    # Add to analysis.html (the posts page)
    analysis_path = os.path.join(os.path.dirname(__file__), "analysis.html")
    with open(analysis_path, "r") as f:
        content = f.read()

    tag_html = " ".join(f'<span class="tag">{t}</span>' for t in post["tags"])
    # Map category display name to data-category slug
    cat_slug = post["category"].lower().replace(" & ", "-").replace(" ", "-").replace("&", "")
    new_card = f"""
      <div class="article-card" data-category="{cat_slug}" onclick="window.location='articles/{post['slug']}.html'" style="animation-delay:0.05s">
        <span class="card-emoji">{post['emoji']}</span>
        <div class="card-category">{post['category']}</div>
        <div class="card-title">{post['title']}</div>
        <p class="card-excerpt">{post['excerpt']}</p>
        <div class="card-meta">
          {tag_html}
          <span>{post['date']}</span>
        </div>
      </div>
"""
    # Insert at top of articles grid
    marker = '<div class="articles-grid" id="articles-grid">'
    updated = content.replace(marker, marker + new_card, 1)

    with open(analysis_path, "w") as f:
        f.write(updated)
    print("✅ analysis.html updated — new card added at top of grid")

    # Also add the card to the Dashboard Analysis tab
    index_path = os.path.join(os.path.dirname(__file__), "index.html")
    with open(index_path, "r") as f:
        idx_content = f.read()

    idx_card = f"""
      <div class="article-card" onclick="window.location='articles/{post['slug']}.html'">
        <span class="card-emoji">{post['emoji']}</span>
        <div class="card-category">{post['category']}</div>
        <div class="card-title">{post['title']}</div>
        <p class="card-excerpt">{post['excerpt']}</p>
        <div class="card-meta">
          {tag_html}
          <span>{post['date']}</span>
        </div>
      </div>
"""
    idx_marker = '<div class="articles-grid" id="articles-grid">'
    idx_updated = idx_content.replace(idx_marker, idx_marker + idx_card, 1)
    with open(index_path, "w") as f:
        f.write(idx_updated)
    print("✅ index.html Analysis tab also updated")


