"""Orchestrate the real-world verification layer."""
from app.verification.search import search
from app.verification.extractor import fetch_page
from app.verification import evidence

def verify(headline: str, article: str) -> dict:
    words = evidence.keywords(headline)
    if len(words) < 2:
        return {'status': 'UNAVAILABLE',
                'summary': 'Real-world verification could not be completed: not enough distinctive claim terms in the headline.',
                'sources': [], 'queries': []}
    queries = []
    queries.append(' '.join(words[:4]))
    queries.append(' '.join(words[:3]) + ' news')
    try:
        results = []
        seen_urls = set()
        for q in queries:
            for r in search(q, limit=4):
                if r['url'] in seen_urls:
                    continue
                seen_urls.add(r['url'])
                results.append(r)
        if not results:
            return {'status': 'UNAVAILABLE',
                    'summary': 'Real-world verification could not be completed: no search results could be retrieved.',
                    'sources': [], 'queries': queries}
        assessments = []
        for r in results[:4]:
            page = fetch_page(r['url'])
            if page and len(page['text']) > 200:
                r.update(title=page['title'] or r['title'], published=page['published'],
                         text=page['text'])
            else:
                r['text'] = r.get('snippet', '')
            assessments.append(evidence.assess_source(words, r))
        status, summary = evidence.summarize(assessments)
        return {'status': status, 'summary': summary, 'sources': assessments, 'queries': queries}
    except Exception:
        return {'status': 'UNAVAILABLE',
                'summary': 'Real-world verification could not be completed due to a network or API failure.',
                'sources': [], 'queries': queries}
