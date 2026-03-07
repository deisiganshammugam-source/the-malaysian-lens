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

import os
import re
from datetime import datetime

# ─────────────────────────────────────────────
# FILL THIS IN FOR EACH NEW POST
# ─────────────────────────────────────────────
POST_DATA = {
    "slug":       "example-post",          # URL-safe filename, no spaces
    "title":      "Your Article Title Here",
    "subtitle":   "The one-line hook that goes under the headline.",
    "category":   "Monetary Policy",        # e.g. Industry & Trade, Labour & Wages, etc.
    "tags":       ["BNM", "DOSM"],          # short tags shown as badges
    "date":       "March 2026",
    "emoji":      "📊",                     # shown as the card thumbnail
    "excerpt":    "Short preview shown on the homepage card.",
    "body_html":  """
        <!-- PASTE YOUR ARTICLE HTML BODY HERE -->
        <!-- Use the blocks below as building blocks: -->

        <!-- HOOK -->
        <p class="hook">Opening hook sentence here.</p>
        <p class="hook-sub">Follow-up sentence that sets the tension.</p>

        <!-- BODY PARAGRAPHS -->
        <p>Your analysis paragraph here.</p>

        <!-- SECTION BREAK -->
        <div class="section-break">· · ·</div>

        <!-- KEY NUMBERS BLOCK (3 stats) -->
        <div class="key-numbers">
          <div class="key-num"><div class="val">X%</div><div class="lbl">Label here</div></div>
          <div class="key-num"><div class="val">RM Xb</div><div class="lbl">Label here</div></div>
          <div class="key-num"><div class="val">X%</div><div class="lbl">Label here</div></div>
        </div>

        <!-- DATA TABLE -->
        <div class="data-table-wrapper">
          <div class="data-table-title">TABLE TITLE</div>
          <table>
            <thead><tr><th>Col 1</th><th>Col 2</th><th>Col 3</th></tr></thead>
            <tbody>
              <tr><td>Row 1A</td><td>Row 1B</td><td>Row 1C</td></tr>
              <tr><td>Row 2A</td><td>Row 2B</td><td>Row 2C</td></tr>
            </tbody>
          </table>
          <div class="table-source">Source: DOSM / BNM — Month Year</div>
        </div>

        <!-- PULL QUOTE -->
        <div class="pull-quote"><p>"Your key quote here."</p></div>

        <!-- CALLOUT BOX (for "if true / if not true" tension) -->
        <div class="callout"><strong>If true:</strong> explanation here.</div>
        <div class="callout" style="border-color:#6b7280;background:#f3f4f6;">
          <strong>If not true:</strong> explanation here.
        </div>

        <!-- VIGILANCE CLOSER (always end with this) -->
        <div class="vigilance-box">
          <p>Don't be tired. Be vigilant. Ask questions. Demand answers.<br/>
          Malaysia has come too far to lose it.</p>
          <span class="flag">🇲🇾</span>
        </div>

        <p class="disclaimer">Views are my own. Data sourced from DOSM, BNM, and publicly available sources.</p>
    """,
    # Sources line shown in footer
    "sources": "Data: DOSM · BNM · World Bank",
}
# ─────────────────────────────────────────────


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


if __name__ == "__main__":
    print(f"\n📰 Publishing: {POST_DATA['title']}")
    print(f"   Slug: {POST_DATA['slug']}")
    print(f"   Date: {POST_DATA['date']}\n")

    make_article(POST_DATA)
    add_to_index(POST_DATA)

    print(f"\n🎉 Done! Open index.html in your browser to preview.")
    print(f"   Article URL: articles/{POST_DATA['slug']}.html\n")
