import sys, os, json
sys.path.insert(0, 'D:/documents/FNDS')
import numpy as np, joblib
from sklearn.metrics import accuracy_score
from ml.pipeline import load_dataset
from sklearn.model_selection import train_test_split

df = load_dataset()
X = df['input']; y = df['label']
_, X_test, _, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
m = joblib.load('D:/documents/FNDS/ml/models/best_model.joblib')
proba = m.predict_proba(X_test)[:, 1]
pred = m.predict(X_test)
sweep = []
for thr in np.arange(0.50, 0.96, 0.05):
    conf = np.maximum(proba, 1 - proba)
    cover = (conf >= thr).mean()
    acc = accuracy_score(y_test[conf >= thr], pred[conf >= thr]) if cover > 0 else None
    sweep.append({'threshold': round(float(thr), 2), 'coverage': round(float(cover), 3),
                  'accuracy_when_confident': round(float(acc), 4) if acc else None})
print(json.dumps(sweep, indent=1))
d = json.load(open('D:/documents/FNDS/ml/reports/evaluation.json'))
d['uncertainty_sweep_best_model'] = sweep
json.dump(d, open('D:/documents/FNDS/ml/reports/evaluation.json', 'w'), indent=2)
