"""Turn search results + extracted pages into a verification verdict.

Everything here is derived from actually retrieved content; nothing is fabricated.
"""
import re
from collections import Counter

STOP = set('''the a an and or of to in on for with by at from is are was were be been this that these those it its as not no new said says report according after before over under into about will would can could may might more most less than how what who when where why do does did has have had amid between while during such'''.split())

NEG_HINTS = ['fake', 'hoax', 'false', 'debunked', 'misinformation', 'fabricated', 'no evidence',
             'not true', 'unfounded', 'rumor', 'rumour', 'misleading', 'disputed', 'correction']

ALIASES = {
    'fed': ['federal reserve', 'fed'],
    'usa': ['united states', 'usa', 'america'],
    'eu': ['european union', 'eu'],
    'uk': ['united kingdom', 'britain', 'uk'],
}

def _word_hit(w: str, t: str) -> bool:
    variants = ALIASES.get(w, [w])
    return any(re.search(r'\b' + re.escape(v) + r'\b', t) for v in variants)

def keywords(headline: str, top_k: int = 8) -> list[str]:
    words = re.findall(r"[A-Za-z][A-Za-z\-']+", headline.lower())
    words = [w for w in words if w not in STOP and len(w) > 2]
    # keep order but unique
    seen, out = set(), []
    for w in words:
        if w not in seen:
            seen.add(w); out.append(w)
    return out[:top_k]

def _overlap(words: list[str], text: str) -> float:
    if not text or not words:
        return 0.0
    t = text.lower()
    hits = sum(1 for w in words if _word_hit(w, t))
    return hits / len(words)

def assess_source(words: list[str], doc: dict) -> dict:
    blob = (doc.get('title', '') + ' ' + doc.get('text', '') + ' ' + doc.get('snippet', ''))
    ov = _overlap(words, blob)
    low = blob.lower()
    neg = any(h in low for h in NEG_HINTS)
    if ov >= 0.5 and neg:
        label = 'CONTRADICTING'
    elif ov >= 0.5:
        label = 'SUPPORTING'
    else:
        label = 'INSUFFICIENT'
    excerpt = (doc.get('text') or doc.get('snippet', ''))[:280]
    return {
        'source': doc.get('source') or doc.get('url', '').split('/')[2],
        'title': doc.get('title', ''),
        'url': doc.get('url', ''),
        'date': doc.get('published', ''),
        'excerpt': excerpt,
        'label': label,
        'relevance': round(ov, 2),
    }

def summarize(source_assessments: list[dict]) -> tuple[str, str]:
    labels = Counter(s['label'] for s in source_assessments)
    n_support = labels.get('SUPPORTING', 0)
    n_contra = labels.get('CONTRADICTING', 0)
    n_insuf = labels.get('INSUFFICIENT', 0)
    if n_contra > 0 and n_contra >= n_support:
        return 'CONTRADICTING', f'{n_contra} retrieved source(s) contain language contradicting the main claim.'
    if n_support >= 2:
        return 'SUPPORTING', f'{n_support} retrieved source(s) report information consistent with the main claim.'
    if n_support == 1:
        return 'SUPPORTING', 'One retrieved source reports information consistent with the main claim; no strong contradiction found.'
    return 'INSUFFICIENT', 'No retrieved source provides enough relevant evidence to confirm or refute the main claim.'
