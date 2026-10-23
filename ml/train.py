"""Train, evaluate, error-analyze and persist fake-news classifiers."""
import sys, os, json, joblib, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, roc_auc_score, confusion_matrix, classification_report)
from sklearn.calibration import CalibratedClassifierCV

from ml.pipeline import load_dataset

SEED = 42

def build_models():
    tfidf = lambda: TfidfVectorizer(ngram_range=(1, 2), min_df=5, max_df=0.9,
                                    max_features=60000, sublinear_tf=True)
    return {
        'LogisticRegression': Pipeline([
            ('tfidf', tfidf()),
            ('clf', LogisticRegression(max_iter=1000, C=1.0, random_state=SEED)),
        ]),
        'LinearSVM': Pipeline([
            ('tfidf', tfidf()),
            ('clf', CalibratedClassifierCV(LinearSVC(C=0.5, random_state=SEED), cv=3)),
        ]),
        'RandomForest': Pipeline([
            ('tfidf', TfidfVectorizer(ngram_range=(1, 1), min_df=10, max_df=0.9,
                                      max_features=30000, sublinear_tf=True)),
            ('clf', RandomForestClassifier(n_estimators=150, n_jobs=-1, random_state=SEED)),
        ]),
    }

def main():
    df = load_dataset()
    print('rows after cleaning/dedupe:', len(df))
    X = df['input']; y = df['label']
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=SEED)

    models = build_models()
    results = {}
    fitted = {}
    for name, model in models.items():
        t0 = time.time()
        model.fit(X_train, y_train)
        pred = model.predict(X_test)
        proba = model.predict_proba(X_test)[:, 1]
        cm = confusion_matrix(y_test, pred)
        tn, fp, fn, tp = cm.ravel()
        cv = StratifiedKFold(5, shuffle=True, random_state=SEED)
        cvs = cross_val_score(model, X_train, y_train, cv=cv, scoring='f1', n_jobs=1)
        res = {
            'accuracy': float(accuracy_score(y_test, pred)),
            'precision': float(precision_score(y_test, pred)),
            'recall': float(recall_score(y_test, pred)),
            'f1': float(f1_score(y_test, pred)),
            'roc_auc': float(roc_auc_score(y_test, proba)),
            'false_positive_rate': float(fp / (fp + tn)),
            'false_negative_rate': float(fn / (fn + tp)),
            'cv_f1_mean': float(cvs.mean()),
            'cv_f1_std': float(cvs.std()),
            'confusion_matrix': cm.tolist(),
            'train_seconds': round(time.time() - t0, 1),
        }
        results[name] = res
        fitted[name] = model
        print(name, json.dumps(res, indent=None))

    # error analysis for best-by-f1 interpretable model (LogisticRegression) and overall best
    best_name = max(results, key=lambda k: (results[k]['f1'], -results[k]['false_positive_rate']))
    print('BEST:', best_name)

    err_model = fitted['LogisticRegression']
    pred = err_model.predict(X_test)
    proba = err_model.predict_proba(X_test)[:, 1]
    test_df = pd.DataFrame({'input': X_test, 'actual': y_test, 'predicted': pred,
                            'confidence': np.maximum(proba, 1 - proba)})
    fp_rows = test_df[(test_df.actual == 0) & (test_df.predicted == 1)].head(25)
    fn_rows = test_df[(test_df.actual == 1) & (test_df.predicted == 0)].head(25)
    fp_rows.to_csv('D:/documents/FNDS/ml/reports/false_positives.csv', index=False)
    fn_rows.to_csv('D:/documents/FNDS/ml/reports/false_negatives.csv', index=False)

    # uncertainty threshold sweep
    sweep = []
    for thr in np.arange(0.50, 0.96, 0.05):
        cover = (np.maximum(proba, 1 - proba) >= thr).mean()
        acc = accuracy_score(y_test[np.maximum(proba, 1 - proba) >= thr],
                             pred[np.maximum(proba, 1 - proba) >= thr]) if cover > 0 else None
        sweep.append({'threshold': round(float(thr), 2), 'coverage': round(float(cover), 3),
                      'accuracy_when_confident': round(float(acc), 4) if acc else None})
    report = {'models': results, 'best_model': best_name,
              'uncertainty_sweep': sweep,
              'seed': SEED, 'rows': len(df)}
    with open('D:/documents/FNDS/ml/reports/evaluation.json', 'w') as f:
        json.dump(report, f, indent=2)

    joblib.dump(fitted[best_name], 'D:/documents/FNDS/ml/models/best_model.joblib')
    meta = {'model_name': best_name, 'label_names': {'0': 'REAL', '1': 'FAKE'},
            'features': 'title + " ||| " + text (TF-IDF 1-2 grams)', 'seed': SEED}
    with open('D:/documents/FNDS/ml/models/model_metadata.json', 'w') as f:
        json.dump(meta, f, indent=2)
    print('saved model:', best_name)

if __name__ == '__main__':
    main()
