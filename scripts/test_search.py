import requests
from bs4 import BeautifulSoup
q = 'Trump 2025 news'
r = requests.post('https://html.duckduckgo.com/html/', data={'q': q},
                  headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}, timeout=15)
print(r.status_code, len(r.text))
soup = BeautifulSoup(r.text, 'html.parser')
for a in soup.select('.result__a')[:5]:
    print(a.get_text(strip=True), '|', a.get('href'))
