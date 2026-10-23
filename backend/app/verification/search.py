"""Search the web for recent relevant sources (Bing HTML)."""
import time, threading, base64, re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, urlparse as _up

_H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                    '(KHTML, like Gecko) Chrome/124.0 Safari/537.36'}
_cache = {}
_cache_lock = threading.Lock()
_CACHE_TTL = 900
_last_call = [0.0]

def _rate_limit():
    with _cache_lock:
        wait = 1.0 - (time.time() - _last_call[0])
        if wait > 0:
            time.sleep(wait)
        _last_call[0] = time.time()

def search(query: str, limit: int = 5) -> list[dict]:
    key = ('search', query, limit)
    with _cache_lock:
        hit = _cache.get(key)
        if hit and time.time() - hit[0] < _CACHE_TTL:
            return hit[1]
    _rate_limit()
    results = []
    try:
        r = requests.get('https://www.bing.com/search', params={'q': query, 'count': 10},
                         headers=_H, timeout=12)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            for li in soup.select('li.b_algo'):
                h = li.select_one('h2 a')
                snippet_el = li.select_one('.b_caption p')
                if not h or not h.get('href'):
                    continue
                url = h['href']
                if 'bing.com/ck/a' in url:
                    try:
                        m = re.search(r'[?&]u=a1([^&]+)', url)
                        if m:
                            pad = m.group(1) + '=' * (-len(m.group(1)) % 4)
                            url = base64.urlsafe_b64decode(pad).decode('utf-8', 'ignore')
                    except Exception:
                        pass
                if not urlparse(url).scheme.startswith('http'):
                    continue
                cite = li.select_one('cite')
                source = cite.get_text(strip=True) if cite else urlparse(url).netloc
                results.append({
                    'title': h.get_text(strip=True),
                    'url': url,
                    'snippet': snippet_el.get_text(strip=True) if snippet_el else '',
                    'source': source,
                })
                if len(results) >= limit:
                    break
    except Exception:
        results = []
    with _cache_lock:
        _cache[key] = (time.time(), results)
    return results
