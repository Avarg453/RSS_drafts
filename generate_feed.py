"""
generate_feed.py

Reads all article JSON files from json_dump/, groups them by Source,
sorts by date descending, and writes a clean index.html to the repo root.

Run this after your RSS fetch script, then commit both json_dump/ and index.html.
"""

import json
import os
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path

JSON_DIR = Path("json_dump")
OUTPUT_FILE = Path("index.html")


def parse_date_from_uid(uid: str) -> datetime:
    """
    Parses dates from uID format: source-YYYY-MM-DD-HH-M-SS
    e.g. boltsmag-2025-11-10-19-9-31
    Falls back to epoch if parsing fails.
    """
    try:
        parts = uid.split("-")
        # Find the first 4-digit year
        for i, part in enumerate(parts):
            if len(part) == 4 and part.isdigit():
                date_parts = parts[i:i+6]
                if len(date_parts) == 6:
                    return datetime(*[int(p) for p in date_parts])
    except Exception:
        pass
    return datetime.fromtimestamp(0)


def load_articles() -> dict[str, list[dict]]:
    """Load all JSON files and group by Source."""
    by_source = defaultdict(list)

    for filepath in JSON_DIR.glob("*.json"):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                article = json.load(f)
            source = article.get("Source", "unknown")
            article["_date"] = parse_date_from_uid(article.get("uID", ""))
            by_source[source].append(article)
        except Exception as e:
            print(f"Skipping {filepath.name}: {e}")

    # Sort each source's articles by date descending
    for source in by_source:
        by_source[source].sort(key=lambda a: a["_date"], reverse=True)

    return dict(sorted(by_source.items()))


def truncate(text: str, max_chars: int = 300) -> str:
    """Return a plain-text excerpt."""
    if not text:
        return ""
    # Strip markdown-ish image lines and extra whitespace
    text = re.sub(r"!\[.*?\]\(.*?\)", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    text = " ".join(text.split())
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rsplit(" ", 1)[0] + "…"


def format_date(dt: datetime) -> str:
    if dt == datetime.fromtimestamp(0):
        return ""
    return dt.strftime("%b %d, %Y · %I:%M %p").replace(" 0", " ")


def escape_attr(s: str) -> str:
    """Escape a string for use in an HTML attribute."""
    return s.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")


def build_html(by_source: dict) -> str:
    total = sum(len(v) for v in by_source.values())
    generated = datetime.now().strftime("%B %d, %Y at %I:%M %p")

    # Build flat search index — embedded as JSON in the page
    search_index = []
    for source, articles in by_source.items():
        for a in articles:
            excerpt = truncate(a.get("content", ""), max_chars=500)
            search_index.append({
                "uid": a.get("uID", ""),
                "title": a.get("title", ""),
                "author": a.get("author", ""),
                "excerpt": excerpt,
                "source": source,
            })
    search_index_json = json.dumps(search_index, ensure_ascii=False)

    # Build source nav pills
    nav_pills = "\n".join(
        f'<a href="#source-{re.sub(r"[^a-z0-9]", "-", s.lower())}" class="pill">'
        f'{s} <span class="pill-count">{len(articles)}</span></a>'
        for s, articles in by_source.items()
    )

    # Build source sections — cards get data-uid for search targeting
    sections = ""
    for source, articles in by_source.items():
        source_slug = re.sub(r"[^a-z0-9]", "-", source.lower())
        cards = ""
        for a in articles:
            excerpt = truncate(a.get("content", ""))
            date_str = format_date(a["_date"])
            author = a.get("author", "")
            uid = a.get("uID", "")
            byline = f'<span class="byline">{author}</span>' if author else ""
            date_tag = f'<span class="date">{date_str}</span>' if date_str else ""
            meta = f'<div class="meta">{byline}{date_tag}</div>' if (author or date_str) else ""

            cards += f"""
            <article class="card" data-uid="{escape_attr(uid)}">
                <a href="{a.get('link', '#')}" target="_blank" rel="noopener" class="card-title">
                    {a.get('title', 'Untitled')}
                </a>
                {meta}
                <p class="excerpt">{excerpt}</p>
                <a href="{a.get('link', '#')}" target="_blank" rel="noopener" class="read-more">
                    Read full article →
                </a>
            </article>"""

        sections += f"""
        <section class="source-section" id="source-{source_slug}">
            <h2 class="source-heading">
                <span class="source-dot"></span>
                <span class="source-label">{source}</span>
                <span class="source-count">{len(articles)} article{"s" if len(articles) != 1 else ""}</span>
            </h2>
            <div class="cards-grid">
                {cards}
            </div>
            <p class="no-results-msg" style="display:none;">No matching articles in this source.</p>
        </section>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Feed Digest</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Source+Serif+4:ital,wght@0,300;0,400;1,300&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg: #0f0e0c;
            --surface: #1a1915;
            --border: #2e2c27;
            --accent: #c8a96e;
            --accent-dim: #8a7045;
            --text: #e8e4db;
            --text-muted: #8a8578;
            --text-faint: #4a4840;
            --card-bg: #161512;
            --radius: 4px;
        }}

        * {{ box-sizing: border-box; margin: 0; padding: 0; }}

        body {{
            background: var(--bg);
            color: var(--text);
            font-family: 'Source Serif 4', Georgia, serif;
            font-weight: 300;
            line-height: 1.7;
            min-height: 100vh;
        }}

        /* Header */
        header {{
            border-bottom: 1px solid var(--border);
            padding: 2.5rem 0 1.25rem;
            position: sticky;
            top: 0;
            background: rgba(15,14,12,0.97);
            backdrop-filter: blur(8px);
            z-index: 100;
        }}

        .header-inner {{
            max-width: 1100px;
            margin: 0 auto;
            padding: 0 2rem;
            display: flex;
            align-items: baseline;
            gap: 1.5rem;
            flex-wrap: wrap;
        }}

        h1 {{
            font-family: 'Playfair Display', Georgia, serif;
            font-size: clamp(1.8rem, 4vw, 2.8rem);
            font-weight: 900;
            letter-spacing: -0.02em;
            color: var(--text);
        }}

        h1 span {{ color: var(--accent); }}

        .header-meta {{
            color: var(--text-muted);
            font-size: 0.85rem;
            margin-left: auto;
            font-style: italic;
        }}

        /* Search bar */
        .search-row {{
            max-width: 1100px;
            margin: 1rem auto 0;
            padding: 0 2rem;
        }}

        .search-wrap {{
            position: relative;
            max-width: 480px;
        }}

        .search-wrap svg {{
            position: absolute;
            left: 0.9rem;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-faint);
            pointer-events: none;
        }}

        #search {{
            width: 100%;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            color: var(--text);
            font-family: 'Source Serif 4', serif;
            font-size: 0.9rem;
            font-weight: 300;
            padding: 0.55rem 2.8rem 0.55rem 2.4rem;
            outline: none;
            transition: border-color 0.15s ease, box-shadow 0.15s ease;
        }}

        #search::placeholder {{ color: var(--text-faint); font-style: italic; }}

        #search:focus {{
            border-color: var(--accent-dim);
            box-shadow: 0 0 0 2px rgba(200,169,110,0.1);
        }}

        .search-clear {{
            position: absolute;
            right: 0.7rem;
            top: 50%;
            transform: translateY(-50%);
            background: none;
            border: none;
            color: var(--text-faint);
            cursor: pointer;
            padding: 0.2rem;
            display: none;
            line-height: 1;
            font-size: 1rem;
        }}

        .search-clear:hover {{ color: var(--text-muted); }}

        #search-status {{
            font-size: 0.78rem;
            color: var(--text-muted);
            font-style: italic;
            margin-top: 0.4rem;
            min-height: 1.2em;
        }}

        #search-status.has-results {{ color: var(--accent-dim); }}
        #search-status.no-results {{ color: #a05050; }}

        /* Nav */
        nav {{
            max-width: 1100px;
            margin: 0 auto;
            padding: 1rem 2rem 0;
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
        }}

        .pill {{
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            padding: 0.3rem 0.9rem;
            border: 1px solid var(--border);
            border-radius: 999px;
            color: var(--text-muted);
            text-decoration: none;
            font-size: 0.78rem;
            font-family: 'Source Serif 4', serif;
            letter-spacing: 0.03em;
            transition: all 0.15s ease;
        }}

        .pill:hover {{
            border-color: var(--accent);
            color: var(--accent);
            background: rgba(200, 169, 110, 0.06);
        }}

        .pill-count {{
            background: var(--border);
            border-radius: 999px;
            padding: 0 0.45rem;
            font-size: 0.7rem;
            color: var(--text-faint);
        }}

        /* Main layout */
        main {{
            max-width: 1100px;
            margin: 0 auto;
            padding: 3rem 2rem 5rem;
        }}

        /* Source sections */
        .source-section {{
            margin-bottom: 4rem;
        }}

        .source-section.search-hidden {{ display: none; }}

        .source-heading {{
            font-family: 'Playfair Display', Georgia, serif;
            font-size: 1.4rem;
            font-weight: 700;
            color: var(--text);
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding-bottom: 0.75rem;
            border-bottom: 1px solid var(--border);
        }}

        .source-dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--accent);
            flex-shrink: 0;
        }}

        .source-count {{
            font-family: 'Source Serif 4', serif;
            font-size: 0.8rem;
            font-weight: 300;
            color: var(--text-muted);
            margin-left: auto;
            font-style: italic;
        }}

        .no-results-msg {{
            font-size: 0.85rem;
            color: var(--text-faint);
            font-style: italic;
            padding: 1rem 0;
        }}

        /* Cards grid */
        .cards-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 1px;
            background: var(--border);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            overflow: hidden;
        }}

        .cards-grid:empty {{ display: none; }}

        .card {{
            background: var(--card-bg);
            padding: 1.5rem;
            display: flex;
            flex-direction: column;
            gap: 0.6rem;
            transition: background 0.15s ease;
        }}

        .card.search-hidden {{ display: none; }}

        .card:hover {{ background: var(--surface); }}

        .card-title {{
            font-family: 'Playfair Display', Georgia, serif;
            font-size: 1.05rem;
            font-weight: 700;
            line-height: 1.35;
            color: var(--text);
            text-decoration: none;
            display: block;
        }}

        .card-title:hover {{ color: var(--accent); }}

        .meta {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
            flex-wrap: wrap;
        }}

        .byline {{
            font-size: 0.78rem;
            color: var(--accent-dim);
            font-style: italic;
        }}

        .date {{
            font-size: 0.73rem;
            color: var(--text-faint);
        }}

        .excerpt {{
            font-size: 0.88rem;
            color: var(--text-muted);
            line-height: 1.65;
            flex: 1;
        }}

        /* Highlight matched text */
        mark {{
            background: rgba(200, 169, 110, 0.25);
            color: var(--accent);
            border-radius: 2px;
            padding: 0 1px;
        }}

        .read-more {{
            font-size: 0.78rem;
            color: var(--accent-dim);
            text-decoration: none;
            letter-spacing: 0.02em;
            margin-top: 0.25rem;
            align-self: flex-start;
        }}

        .read-more:hover {{ color: var(--accent); }}

        /* Global empty state */
        #global-empty {{
            display: none;
            text-align: center;
            padding: 5rem 2rem;
            color: var(--text-faint);
        }}

        #global-empty strong {{
            display: block;
            font-family: 'Playfair Display', serif;
            font-size: 1.3rem;
            color: var(--text-muted);
            margin-bottom: 0.5rem;
        }}

        /* Footer */
        footer {{
            text-align: center;
            padding: 2rem;
            color: var(--text-faint);
            font-size: 0.78rem;
            border-top: 1px solid var(--border);
            font-style: italic;
        }}

        @media (max-width: 600px) {{
            .cards-grid {{ grid-template-columns: 1fr; }}
            .header-inner {{ flex-direction: column; gap: 0.25rem; }}
            .header-meta {{ margin-left: 0; }}
            .search-wrap {{ max-width: 100%; }}
        }}
    </style>
</head>
<body>

<header>
    <div class="header-inner">
        <h1>Feed <span>Digest</span></h1>
        <span class="header-meta">{total} articles · updated {generated}</span>
    </div>
    <div class="search-row">
        <div class="search-wrap">
            <svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M10 6.5a3.5 3.5 0 1 1-7 0 3.5 3.5 0 0 1 7 0Zm-.691 3.516a4.5 4.5 0 1 1 .707-.707l2.838 2.837a.5.5 0 0 1-.708.708L9.31 10.016Z" fill="currentColor"/>
            </svg>
            <input id="search" type="search" placeholder="Search title, author, content…" autocomplete="off" spellcheck="false">
            <button class="search-clear" id="search-clear" title="Clear search">✕</button>
        </div>
        <div id="search-status"></div>
    </div>
    <nav>
        {nav_pills}
    </nav>
</header>

<main>
    {sections}
    <div id="global-empty">
        <strong>No results found</strong>
        Try a different search term
    </div>
</main>

<footer>
    Generated automatically · {generated}
</footer>

<script>
const INDEX = {search_index_json};

// Build a uid -> card element map once
const cardMap = {{}};
document.querySelectorAll('.card[data-uid]').forEach(el => {{
    cardMap[el.dataset.uid] = el;
}});

const searchInput = document.getElementById('search');
const clearBtn = document.getElementById('search-clear');
const statusEl = document.getElementById('search-status');
const globalEmpty = document.getElementById('global-empty');

function escapeRe(s) {{
    return s.replace(/[.*+?^${{}}()|[\\]\\\\]/g, '\\\\$&');
}}

function highlight(text, term) {{
    if (!term) return text;
    const re = new RegExp('(' + escapeRe(term) + ')', 'gi');
    return text.replace(re, '<mark>$1</mark>');
}}

// Find the best ~200-char window in text that contains the term
function contextSnippet(text, term, radius) {{
    const lower = text.toLowerCase();
    const idx = lower.indexOf(term.toLowerCase());
    if (idx === -1) return text.slice(0, radius * 2) + '…';
    const start = Math.max(0, idx - radius);
    const end = Math.min(text.length, idx + term.length + radius);
    return (start > 0 ? '…' : '') + text.slice(start, end) + (end < text.length ? '…' : '');
}}

let debounceTimer;

function runSearch(term) {{
    term = term.trim();
    clearBtn.style.display = term ? 'block' : 'none';

    if (!term) {{
        resetAll();
        return;
    }}

    const lower = term.toLowerCase();
    const matchedUids = new Set();

    // Score each article
    INDEX.forEach(item => {{
        const inTitle   = item.title.toLowerCase().includes(lower);
        const inAuthor  = item.author.toLowerCase().includes(lower);
        const inExcerpt = item.excerpt.toLowerCase().includes(lower);
        if (inTitle || inAuthor || inExcerpt) matchedUids.add(item.uid);
    }});

    let totalVisible = 0;

    // Show/hide cards and update excerpts
    document.querySelectorAll('.card[data-uid]').forEach(card => {{
        const uid = card.dataset.uid;
        if (matchedUids.has(uid)) {{
            card.classList.remove('search-hidden');
            totalVisible++;

            // Update excerpt with highlighted context snippet
            const item = INDEX.find(i => i.uid === uid);
            if (item) {{
                const excerptEl = card.querySelector('.excerpt');
                const titleEl   = card.querySelector('.card-title');
                const bylineEl  = card.querySelector('.byline');

                // Highlight title
                if (titleEl) titleEl.innerHTML = highlight(item.title, term);

                // Highlight author
                if (bylineEl) bylineEl.innerHTML = highlight(item.author, term);

                // Show contextual excerpt with highlight
                if (excerptEl) {{
                    const snippet = contextSnippet(item.excerpt, term, 120);
                    excerptEl.innerHTML = highlight(snippet, term);
                }}
            }}
        }} else {{
            card.classList.add('search-hidden');
        }}
    }});

    // Show/hide sections and their "no results" messages
    let visibleSections = 0;
    document.querySelectorAll('.source-section').forEach(section => {{
        const visibleCards = section.querySelectorAll('.card:not(.search-hidden)').length;
        const noResultsMsg = section.querySelector('.no-results-msg');
        const grid = section.querySelector('.cards-grid');
        if (visibleCards === 0) {{
            section.classList.add('search-hidden');
        }} else {{
            section.classList.remove('search-hidden');
            visibleSections++;
        }}
        if (noResultsMsg) noResultsMsg.style.display = visibleCards === 0 ? 'block' : 'none';
    }});

    globalEmpty.style.display = totalVisible === 0 ? 'block' : 'none';

    // Update status
    if (totalVisible === 0) {{
        statusEl.textContent = 'No results for "' + term + '"';
        statusEl.className = 'no-results';
    }} else {{
        statusEl.textContent = totalVisible + ' result' + (totalVisible === 1 ? '' : 's') + ' for "' + term + '"';
        statusEl.className = 'has-results';
    }}
}}

function resetAll() {{
    document.querySelectorAll('.card').forEach(card => {{
        card.classList.remove('search-hidden');
        // Restore original excerpt text (stored in data-original-* on first search)
        const excerptEl = card.querySelector('.excerpt');
        const titleEl   = card.querySelector('.card-title');
        const bylineEl  = card.querySelector('.byline');
        const uid = card.dataset.uid;
        const item = INDEX.find(i => i.uid === uid);
        if (item && excerptEl) excerptEl.textContent = item.excerpt.slice(0, 300);
        if (item && titleEl)   titleEl.textContent   = item.title;
        if (item && bylineEl)  bylineEl.textContent  = item.author;
    }});
    document.querySelectorAll('.source-section').forEach(s => {{
        s.classList.remove('search-hidden');
        const msg = s.querySelector('.no-results-msg');
        if (msg) msg.style.display = 'none';
    }});
    globalEmpty.style.display = 'none';
    statusEl.textContent = '';
    statusEl.className = '';
}}

// Live filter as you type (debounced 150ms)
searchInput.addEventListener('input', () => {{
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => runSearch(searchInput.value), 150);
}});

// Enter key triggers immediately
searchInput.addEventListener('keydown', (e) => {{
    if (e.key === 'Enter') {{
        clearTimeout(debounceTimer);
        runSearch(searchInput.value);
    }}
    if (e.key === 'Escape') {{
        searchInput.value = '';
        resetAll();
        clearBtn.style.display = 'none';
    }}
}});

clearBtn.addEventListener('click', () => {{
    searchInput.value = '';
    resetAll();
    clearBtn.style.display = 'none';
    searchInput.focus();
}});

// Keyboard shortcut: "/" focuses search
document.addEventListener('keydown', (e) => {{
    if (e.key === '/' && document.activeElement !== searchInput) {{
        e.preventDefault();
        searchInput.focus();
    }}
}});
</script>

</body>
</html>"""


def main():
    if not JSON_DIR.exists():
        print(f"Error: '{JSON_DIR}' directory not found. Run from your repo root.")
        return

    print(f"Reading articles from {JSON_DIR}/...")
    by_source = load_articles()

    total = sum(len(v) for v in by_source.values())
    print(f"Found {total} articles across {len(by_source)} sources: {', '.join(by_source.keys())}")

    html = build_html(by_source)
    OUTPUT_FILE.write_text(html, encoding="utf-8")
    print(f"Written to {OUTPUT_FILE} ({OUTPUT_FILE.stat().st_size // 1024}KB)")
    print("\nNext steps:")
    print("  git add index.html")
    print("  git commit -m 'Update feed digest'")
    print("  git push")


if __name__ == "__main__":
    main()
