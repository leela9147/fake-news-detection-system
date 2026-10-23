"""Responsible page extraction: robots.txt-respecting, cached, rate-limited."""
import time, threading, urllib.robotparser
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

_H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                    '(KHTML, like Gecko) Chrome/124.0 Safari/537.36'}
_cache = {}
_lock = threading.Lock()
_TTL = 3600
_last_fetch = [0.0]

def _allowed(url: str) -> bool:
    try:
        p = urlparse(url)
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(f'{p.scheme}://{p.netloc}/robots.txt')
        rp.read()
        return rp.can_fetch(_H['User-Agent'], url)
    except Exception:
        return True  # if robots cannot be fetched, fall back to polite fetch

def fetch_page(url: str, max_chars: int = 6000) -> dict | None:
    with _lock:
        hit = _cache.get(url)
        if hit and time.time() - hit[0] < _TTL:
            return hit[1]
    if not _allowed(url):
        return None
    with _lock:
        wait = 1.0 - (time.time() - _last_fetch[0])
        if wait > 0:
            time.sleep(wait)
        _last_fetch[0] = time.time()
    try:
        r = requests.get(url, headers=_H, timeout=6, allow_redirects=True)
        if r.status_code != 200 or 'text/html' not in r.headers.get('content-type', ''):
            return None
        soup = BeautifulSoup(r.text, 'html.parser')
        for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'form', 'noscript']):
            tag.decompose()
        title = soup.title.get_text(strip=True) if soup.title else ''
        # publication date heuristic
        pub = ''
        for key in ['article:published_time', 'datePublished', 'pubdate', 'publishdate']:
            el = soup.find('meta', attrs={'property': key}) or soup.find('meta', attrs={'name': key})
            if el and el.get('content'):
                pub = el['content'][:32]
                break
        text = ' '.join(soup.stripped_strings)
        text = text[:max_chars]
        out = {'title': title, 'text': text, 'published': pub, 'url': url}
        with _lock:
            _cache[url] = (time.time(), out)
        return out
    except Exception:
        return None
