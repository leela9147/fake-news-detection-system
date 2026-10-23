"""Load the trained model once and serve predictions + explanations."""
import json, os, sys
import numpy as np
import joblib
from app.config import MODEL_PATH, METADATA_PATH, CONFIDENCE_THRESHOLD

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from ml.pipeline import clean_text

_model = None
_meta = None

def get_model():
    global _model, _meta
    if _model is None:
        _model = joblib.load(MODEL_PATH)
        with open(METADATA_PATH) as f:
            _meta = json.load(f)
    return _model, _meta

def _feature_weights(model):
    """Average linear coefficients across the calibrated sub-estimators."""
    clf = model.named_steps['clf']
    coefs = []
    if hasattr(clf, 'calibrated_classifiers_'):
        for cc in clf.calibrated_classifiers_:
            est = cc.estimator
            if hasattr(est, 'coef_'):
                coefs.append(est.coef_.ravel())
    elif hasattr(clf, 'coef_'):
        coefs.append(clf.coef_.ravel())
    return np.mean(coefs, axis=0) if coefs else None

def predict_and_explain(headline: str, article: str):
    model, meta = get_model()
    text_input = clean_text(headline) + ' ||| ' + clean_text(article)
    proba = model.predict_proba([text_input])[0]
    p_fake, p_real = float(proba[1]), float(proba[0])
    pred_label = int(p_fake >= p_real)
    confidence = max(p_fake, p_real)

    if confidence < CONFIDENCE_THRESHOLD:
        ml_result = 'NEEDS VERIFICATION'
        confidence_word = f"{confidence*100:.0f}% model confidence — below the {CONFIDENCE_THRESHOLD*100:.0f}% confidence threshold"
    elif pred_label == 1:
        ml_result = 'LIKELY FAKE'
        confidence_word = f"{confidence*100:.0f}% model confidence"
    else:
        ml_result = 'LIKELY REAL'
        confidence_word = f"{confidence*100:.0f}% model confidence"

    # feature contributions
    tfidf = model.named_steps['tfidf']
    vec = tfidf.transform([text_input])
    coefs = _feature_weights(model)
    signals = []
    tech_features = []
    if coefs is not None:
        contrib = vec.toarray()[0] * coefs
        idx = np.where(vec.toarray()[0] > 0)[0]
        scored = [(contrib[i], tfidf.get_feature_names_out()[i]) for i in idx]
        top_fake = sorted(scored, key=lambda x: x[0], reverse=True)[:8]
        top_real = sorted(scored, key=lambda x: x[0])[:8]
        if pred_label == 1:
            for v, name in top_fake:
                if v > 0:
                    signals.append(name)
                    tech_features.append({'feature': name, 'contribution': round(float(v), 4),
                                          'direction': 'supports LIKELY FAKE'})
        else:
            for v, name in top_real:
                if v < 0:
                    signals.append(name)
                    tech_features.append({'feature': name, 'contribution': round(float(v), 4),
                                          'direction': 'supports LIKELY REAL'})
        signals = signals[:6]

    if ml_result == 'LIKELY FAKE':
        simple = ('The AI found several language patterns in this article that are more commonly '
                  'associated with examples of unreliable or misleading news in the material it '
                  'learned from. This is a statistical pattern-match, not proof.')
    elif ml_result == 'LIKELY REAL':
        simple = ('The AI found language patterns in this article that are more commonly '
                  'associated with examples of reliable news in the material it learned from. '
                  'This is a statistical pattern-match, not proof.')
    else:
        simple = ('The AI is not confident enough to classify this article as clearly real or '
                  'fake. This can happen for unusual, mixed, or out-of-distribution writing.')

    technical = {
        'model_name': meta.get('model_name', 'unknown'),
        'raw_decision_probs': {'REAL': round(p_real, 4), 'FAKE': round(p_fake, 4)},
        'confidence_threshold': CONFIDENCE_THRESHOLD,
        'top_feature_contributions': tech_features,
        'tfidf': 'sublinear TF-IDF, unigrams+bigrams, fitted on training data only',
    }
    return {
        'ml_prediction': ml_result,
        'ml_confidence': round(confidence * 100, 1),
        'ml_confidence_wording': confidence_word,
        'model_name': meta.get('model_name', 'unknown'),
        'simple_explanation': simple,
        'signals': signals,
        'technical_explanation': technical,
    }
