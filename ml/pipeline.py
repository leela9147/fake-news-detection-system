"""Shared preprocessing + feature building for the FNDS ML pipeline."""
import re
import pandas as pd

_HTML = re.compile(r'<[^>]+>')
_WS = re.compile(r'\s+')
_URL = re.compile(r'https?://\S+|www\.\S+')

def clean_text(s: str) -> str:
    if not isinstance(s, str):
        return ''
    s = _HTML.sub(' ', s)
    s = _URL.sub(' ', s)
    s = s.replace('\u00e2\u20ac\u2122', "'").replace('\u00e2\u20ac\u0153', '"').replace('\u00e2\u20ac\x9d', '"')
    s = _WS.sub(' ', s)
    return s.strip()

def load_dataset():
    fake = pd.read_csv('D:/documents/FNDS/data/raw/FakeNews.csv')
    fake['label'] = 1; fake['label_name'] = 'FAKE'
    real = pd.read_csv('D:/documents/FNDS/data/raw/TrueNews.csv')
    real['label'] = 0; real['label_name'] = 'REAL'
    df = pd.concat([fake, real], ignore_index=True)
    df['title'] = df['title'].fillna('').map(clean_text)
    df['text'] = df['text'].fillna('').map(clean_text)
    df = df[(df['text'].str.len() > 0)]
    # deduplicate on article text (exact) to avoid train/test leakage
    df = df.drop_duplicates(subset=['text']).reset_index(drop=True)
    df['input'] = df['title'] + ' ||| ' + df['text']
    return df
