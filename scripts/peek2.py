import pandas as pd
df = pd.read_csv('D:/documents/FNDS/data/processed/combined_clean.csv', nrows=20000)
print(df.columns.tolist())
print(df.head(2).to_string())
print(df['label_name'].value_counts())
print(df['source_file'].value_counts())
