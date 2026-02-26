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

# ── Theme selector ─────────────────────────────────────────────────────────
# Change this one value to switch the entire page theme.
# Options: "parchment" | "ink" | "slate" | "forest" | "ivory" | "dusk"
THEME = "parchment"

THEMES = {
    # Warm cream, old newspaper feel
    "parchment": {
        "font_url": "https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Source+Serif+4:ital,wght@0,300;0,400;1,300&family=IBM+Plex+Mono:wght@400&display=swap",
        "header_bg": "rgba(245,240,232,0.97)",
        "heading_font": "'Playfair Display', Georgia, serif",
        "body_font": "'Source Serif 4', Georgia, serif",
        "vars": """
            --bg: #f5f0e8;
            --surface: #ede8dc;
            --border: #d4c9b0;
            --accent: #8b6e3a;
            --accent-dim: #6a5028;
            --text: #081849;
            --text-muted: #120602;
            --text-faint: #213885;
            --card-bg: #f9f5ee;
            --radius: 4px;
        """,
        "mark_bg": "rgba(139,110,58,0.18)",
        "mark_color": "#5a3e1b",
        "pill_hover_bg": "rgba(139,110,58,0.08)",
    },
    # Dark gold editorial (original)
    "ink": {
        "font_url": "https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Source+Serif+4:ital,wght@0,300;0,400;1,300&display=swap",
        "header_bg": "rgba(15,14,12,0.97)",
        "heading_font": "'Playfair Display', Georgia, serif",
        "body_font": "'Source Serif 4', Georgia, serif",
        "vars": """
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
        """,
        "mark_bg": "rgba(200,169,110,0.25)",
        "mark_color": "#c8a96e",
        "pill_hover_bg": "rgba(200,169,110,0.06)",
    },
    # Cool blue-grey modern magazine
    "slate": {
        "font_url": "https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=Literata:ital,wght@0,300;0,400;1,300&family=Syne:wght@700;800&display=swap",
        "header_bg": "rgba(240,242,245,0.97)",
        "heading_font": "'DM Serif Display', Georgia, serif",
        "body_font": "'Literata', Georgia, serif",
        "vars": """
            --bg: #f0f2f5;
            --surface: #e4e8f0;
            --border: #d0d8e8;
            --accent: #2a4a80;
            --accent-dim: #4a6fa5;
            --text: #1a2030;
            --text-muted: #6878a0;
            --text-faint: #a0aac0;
            --card-bg: #f7f9fc;
            --radius: 4px;
        """,
        "mark_bg": "rgba(42,74,128,0.15)",
        "mark_color": "#2a4a80",
        "pill_hover_bg": "rgba(42,74,128,0.06)",
    },
    # Deep green, calm long-read
    "forest": {
        "font_url": "https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=Literata:ital,wght@0,300;0,400;1,300&family=IBM+Plex+Mono:wght@400&display=swap",
        "header_bg": "rgba(14,26,20,0.97)",
        "heading_font": "'DM Serif Display', Georgia, serif",
        "body_font": "'Literata', Georgia, serif",
        "vars": """
            --bg: #0e1a14;
            --surface: #162210;
            --border: #1e3428;
            --accent: #6abf7e;
            --accent-dim: #3a8a58;
            --text: #d4e8d8;
            --text-muted: #4a7a58;
            --text-faint: #2a4a38;
            --card-bg: #111e18;
            --radius: 4px;
        """,
        "mark_bg": "rgba(106,191,126,0.2)",
        "mark_color": "#6abf7e",
        "pill_hover_bg": "rgba(106,191,126,0.06)",
    },
    # Clean white, minimal luxury with red accent
    "ivory": {
        "font_url": "https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,700&family=Source+Serif+4:ital,wght@0,300;0,400;1,300&family=Syne:wght@700;800&display=swap",
        "header_bg": "rgba(254,252,248,0.97)",
        "heading_font": "'Playfair Display', Georgia, serif",
        "body_font": "'Source Serif 4', Georgia, serif",
        "vars": """
            --bg: #fefcf8;
            --surface: #f5f2ec;
            --border: #ece8e0;
            --accent: #c0392b;
            --accent-dim: #962d22;
            --text: #1a1814;
            --text-muted: #9a9088;
            --text-faint: #c8c0b8;
            --card-bg: #fefcf8;
            --radius: 4px;
        """,
        "mark_bg": "rgba(192,57,43,0.12)",
        "mark_color": "#c0392b",
        "pill_hover_bg": "rgba(192,57,43,0.06)",
    },
    # Purple-grey twilight
    "dusk": {
        "font_url": "https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Literata:ital,wght@0,300;0,400;1,300&family=Syne:wght@700;800&display=swap",
        "header_bg": "rgba(22,18,30,0.97)",
        "heading_font": "'Playfair Display', Georgia, serif",
        "body_font": "'Literata', Georgia, serif",
        "vars": """
            --bg: #16121e;
            --surface: #1e1828;
            --border: #2a2040;
            --accent: #a07fd0;
            --accent-dim: #5a3a9a;
            --text: #d8d0e8;
            --text-muted: #6858a0;
            --text-faint: #3a3060;
            --card-bg: #130f1a;
            --radius: 4px;
        """,
        "mark_bg": "rgba(160,127,208,0.2)",
        "mark_color": "#a07fd0",
        "pill_hover_bg": "rgba(160,127,208,0.06)",
    },
}


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
    # Strip markdown images: ![alt](url)
    text = re.sub(r"!\[.*?\]\(.*?\)", "", text)
    # Strip Substack CDN image URLs (bare URLs on their own or inside brackets)
    text = re.sub(r"https?://substackcdn\.com\S+", "", text)
    text = re.sub(r"https?://substack-post-media\S+", "", text)
    # Strip any remaining bare URLs (http/https)
    text = re.sub(r"https?://\S+", "", text)
    # Strip markdown links but keep the label: [label](url) → label
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    # Strip leftover brackets and Substack image captions
    text = re.sub(r"\[!\[.*?\]\]", "", text)
    # Strip any leftover empty link remnants like []( or [](
    text = re.sub(r"\[?\]\s*\(?\s*\)?", "", text)
    # Collapse whitespace
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


def build_html(by_source: dict, theme_name: str = "parchment") -> str:
    total = sum(len(v) for v in by_source.values())
    generated = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    t = THEMES.get(theme_name, THEMES["parchment"])

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
                <button class="source-toggle" aria-label="Toggle {source}">▾</button>
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
    <link href="https://fonts.googleapis.com/css2?family=Cal+Sans&family=Source+Serif+4:ital,wght@0,300;0,400;1,300&family=IBM+Plex+Mono:wght@400&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="style.css">
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

// Collapsible source sections (mobile)
function isMobile() {{ return window.innerWidth <= 700; }}

document.querySelectorAll('.source-heading').forEach(heading => {{
    heading.addEventListener('click', (e) => {{
        if (!isMobile()) return;
        // Don't collapse if user clicked a link inside heading
        if (e.target.tagName === 'A') return;
        const section = heading.closest('.source-section');
        section.classList.toggle('collapsed');
    }});
}});

// On mobile, collapse all sources by default except the first
function initCollapse() {{
    if (!isMobile()) return;
    document.querySelectorAll('.source-section').forEach((s, i) => {{
        if (i > 0) s.classList.add('collapsed');
    }});
}}

initCollapse();
// Re-run if screen is resized from desktop to mobile
window.addEventListener('resize', () => {{
    if (isMobile()) {{
        // Ensure toggle buttons are visible but don't re-collapse already-open sections
    }} else {{
        // Remove all collapsed states when returning to desktop
        document.querySelectorAll('.source-section').forEach(s => {{
            s.classList.remove('collapsed');
        }});
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

    html = build_html(by_source, theme_name=THEME)
    OUTPUT_FILE.write_text(html, encoding="utf-8")
    print(f"Written to {OUTPUT_FILE} ({OUTPUT_FILE.stat().st_size // 1024}KB)")
    print("\nNext steps:")
    print("  git add index.html")
    print("  git commit -m 'Update feed digest'")
    print("  git push")


if __name__ == "__main__":
    main()
