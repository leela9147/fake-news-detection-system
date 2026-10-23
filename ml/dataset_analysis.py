"""Dataset analysis report for the raw Fake/True news datasets."""
import pandas as pd
import json
import os

def load(path, label_name, label):
    df = pd.read_csv(path)
    df['label'] = label
    df['label_name'] = label_name
    df['source_file'] = os.path.basename(path)
    return df

fake = load('D:/documents/FNDS/data/raw/FakeNews.csv', 'FAKE', 1)
real = load('D:/documents/FNDS/data/raw/TrueNews.csv', 'REAL', 0)

report = {}
for name, df in [('fake', fake), ('real', real)]:
    report[name] = {
        'rows': int(len(df)),
        'columns': df.columns.tolist(),
        'missing': df.isna().sum().to_dict(),
        'duplicate_titles': int(df['title'].duplicated().sum()),
        'duplicate_texts': int(df['text'].duplicated().sum()),
        'subjects': df['subject'].value_counts().to_dict(),
        'title_len_mean': float(df['title'].str.len().mean()),
        'text_len_mean': float(df['text'].str.len().mean()),
        'title_len_median': float(df['title'].str.len().median()),
        'text_len_median': float(df['text'].str.len().median()),
    }

combined = pd.concat([fake, real], ignore_index=True)
report['combined'] = {
    'rows': int(len(combined)),
    'class_balance': combined['label_name'].value_counts().to_dict(),
    'duplicate_texts': int(combined['text'].duplicated().sum()),
    'missing_text': int(combined['text'].isna().sum()),
    'missing_title': int(combined['title'].isna().sum()),
    'empty_text': int((combined['text'].fillna('').str.strip() == '').sum()),
    'empty_title': int((combined['title'].fillna('').str.strip() == '').sum()),
}

print(json.dumps(report, indent=2))
with open('D:/documents/FNDS/ml/reports/dataset_analysis.json', 'w') as f:
    json.dump(report, f, indent=2)
