import feedparser
import html2text
import json
import re
from urllib.parse import urlparse
from pathlib import Path
import os

h = html2text.HTML2Text()

RSS_FEEDS = [
    "https://boltsmag.org/feed/",
    "https://www.thebignewsletter.com/feed",
    "https://www.counterpunch.org/feed/",
    "https://jacobinlat.com/feed/", 
    "https://www.kenklippenstein.com/feed", 
    "https://zeteo.com/feed", 
    "https://www.leefang.com/feed", 
    "https://www.propublica.org/feed", 
    "https://mexicosolidarity.com/feed/", 
    "https://www.compactmag.com/feed/"
]

JSON_DUMP_DIR = Path('json_dump')
JSON_DUMP_DIR.mkdir(exist_ok=True)


def extract_domain(url):
    """Extract main domain name from URL."""
    domain_parts = urlparse(url).netloc.split('.')
    return max(domain_parts, key=len)


def format_date(date_tuple):
    """Convert date tuple to YYYY-MM-DD string."""
    return '-'.join(str(elem) for elem in date_tuple[:6])


def decode_unicode_escapes(text):
    """Decode unicode escape sequences like \\u2019 to actual characters."""
    if not isinstance(text, str):
        return text
    
    # Find all \uXXXX patterns and decode them
    def replace_unicode(match):
        code = match.group(1)
        return chr(int(code, 16))
    
    # Replace \uXXXX with actual Unicode character
    return re.sub(r'\\u([0-9a-fA-F]{4})', replace_unicode, text)


def fetch_and_save_feeds():
    """Fetch RSS feeds and save entries as JSON files."""
    for feed_url in RSS_FEEDS:
        rss_feed = feedparser.parse(feed_url)
        for entry in rss_feed.entries:
            source = extract_domain(entry['link'])
            date_str = format_date(entry['published_parsed'])
            uniq_id = f"{source}-{date_str}"

            entry_data = {
                'uID': uniq_id,
                'Source': source,
                'link': entry['link'],
                'title': entry['title'],
                'author': entry.get('author', ''),
                'content': h.handle(entry['content'][0]['value'])
            }

            json_file = JSON_DUMP_DIR / f"{uniq_id}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(entry_data, f, ensure_ascii=False, indent=4)


def fix_unicode_escapes(data, keys=None):
    """Fix unicode escape sequences in specified keys."""
    if keys is None:
        keys = ['title', 'author', 'content']
    
    modified = False
    for key in keys:
        if key in data and isinstance(data[key], str):
            original = data[key]
            fixed = decode_unicode_escapes(original)
            
            if fixed != original:
                data[key] = fixed
                modified = True
    
    return modified


def update_json_files():
    """Update existing JSON files with missing or fixed fields."""
    updated_count = 0
    fixed_count = 0

    for json_file in JSON_DUMP_DIR.glob('*.json'):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Fix unicode issues
        if fix_unicode_escapes(data):
            fixed_count += 1
        
        # Add Source key if missing
        if 'Source' not in data:
            data['Source'] = data['uID'].split('-')[0]
            updated_count += 1
        
        # Save updated file
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    
    print(f"Updated files: {updated_count}, Fixed unicode: {fixed_count}")


if __name__ == '__main__':
    fetch_and_save_feeds()
    update_json_files()
