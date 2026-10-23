import pandas as pd, json

f = pd.read_csv('D:/documents/FNDS/data/raw/FakeNews.csv', nrows=5)
t = pd.read_csv('D:/documents/FNDS/data/raw/TrueNews.csv', nrows=5)
print(f.columns.tolist(), t.columns.tolist())
print(f[['subject','date']].head().to_string())
print(t[['subject','date']].head().to_string())
print(f['text'].iloc[0][:500])
print('---- TRUE ----')
print(t['text'].iloc[0][:500])

# row counts
import os
def count_lines(p):
    c=0
    with open(p,'rb') as fh:
        for _ in fh: c+=1
    return c-1
print('fake rows ~', count_lines('D:/documents/FNDS/data/raw/FakeNews.csv'))
print('true rows ~', count_lines('D:/documents/FNDS/data/raw/TrueNews.csv'))
