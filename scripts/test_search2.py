import requests
from bs4 import BeautifulSoup
H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'}
# try lite
r = requests.post('https://lite.duckduckgo.com/lite/', data={'q': 'Trump 2025 news'}, headers=H, timeout=15)
print('lite', r.status_code, len(r.text))
s = BeautifulSoup(r.text, 'html.parser')
for a in s.select('a.result-link')[:5]:
    print(' ', a.get_text(strip=True), a.get('href'))
# try Wikipedia opensearch
r2 = requests.get('https://en.wikipedia.org/w/api.php', params={'action':'opensearch','search':'Trump 2025','limit':5,'format':'json'}, headers=H, timeout=15)
print('wiki', r2.status_code, r2.text[:300])
# try bing
r3 = requests.get('https://www.bing.com/search', params={'q':'Trump 2025 news'}, headers=H, timeout=15)
print('bing', r3.status_code, len(r3.text))
if r3.status_code == 200:
    s3 = BeautifulSoup(r3.text, 'html.parser')
    for li in s3.select('li.b_algo')[:5]:
        h = li.select_one('h2 a')
        if h: print(' ', h.get_text(strip=True), h.get('href'))
