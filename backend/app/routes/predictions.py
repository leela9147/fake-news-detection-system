from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc
from app.database import get_db
from app.models import User, Prediction
from app.schemas import PredictIn
from app.auth.deps import get_current_user
from app.ml.service import predict_and_explain
from app.verification.verifier import verify

router = APIRouter(prefix='/api', tags=['predictions'])

def final_assessment(ml_result: str, ver_status: str, ml_conf: float) -> tuple[str, str]:
    if ver_status == 'UNAVAILABLE':
        return 'NEEDS VERIFICATION', ('Real-world verification could not be completed, so the system cannot '
               f'cross-check the ML result ({ml_result}). Treat this as needing manual verification.')
    if ml_result == 'NEEDS VERIFICATION':
        return 'NEEDS VERIFICATION', 'The model was not confident enough, and external evidence must help decide.'
    if ml_result == 'LIKELY REAL' and ver_status == 'SUPPORTING':
        return 'LIKELY REAL', 'The ML model leans real and current sources appear to support the main claim.'
    if ml_result == 'LIKELY FAKE' and ver_status == 'CONTRADICTING':
        return 'LIKELY FAKE', 'The ML model leans fake and current sources contain contradicting language.'
    if ml_result == 'LIKELY FAKE' and ver_status == 'SUPPORTING':
        return 'NEEDS VERIFICATION', ('The machine-learning model classified the article as likely fake based on patterns learned from its training data. '
               'However, current external sources appear to support the reported event. This may be a false positive.')
    if ml_result == 'LIKELY REAL' and ver_status == 'CONTRADICTING':
        return 'NEEDS VERIFICATION', ('The ML model leans real, but current sources contain contradicting language. '
               'Treat this as needing manual verification.')
    return 'NEEDS VERIFICATION', 'The available evidence is insufficient or the ML result and evidence conflict.'

def _pred_to_dict(p: Prediction):
    return {
        'id': p.id, 'headline': p.headline, 'article_content': p.article_content,
        'ml_prediction': p.ml_prediction, 'ml_confidence': p.ml_confidence,
        'model_name': p.model_name, 'simple_explanation': p.simple_explanation,
        'technical_explanation': p.technical_explanation,
        'verification_status': p.verification_status,
        'verification_summary': p.verification_summary, 'sources': p.sources,
        'final_assessment': p.final_assessment, 'created_at': p.created_at.isoformat() if p.created_at else '',
    }

@router.post('/predict')
def predict(body: PredictIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        ml = predict_and_explain(body.headline, body.article_content)
    except Exception:
        raise HTTPException(status_code=500, detail='The model could not process this input.')
    try:
        ver = verify(body.headline, body.article_content)
    except Exception:
        ver = {'status': 'UNAVAILABLE',
               'summary': 'Real-world verification could not be completed.',
               'sources': [], 'queries': []}
    fa, fa_expl = final_assessment(ml['ml_prediction'], ver['status'], ml['ml_confidence'])
    p = Prediction(
        user_id=user.id, headline=body.headline, article_content=body.article_content,
        ml_prediction=ml['ml_prediction'], ml_confidence=ml['ml_confidence'],
        model_name=ml['model_name'], simple_explanation=ml['simple_explanation'],
        technical_explanation={**ml['technical_explanation'], 'signals': ml['signals'],
                               'confidence_wording': ml['ml_confidence_wording'],
                               'final_assessment_explanation': fa_expl,
                               'queries': ver.get('queries', [])},
        verification_status=ver['status'], verification_summary=ver['summary'],
        sources=ver['sources'], final_assessment=fa)
    db.add(p); db.commit(); db.refresh(p)
    out = _pred_to_dict(p)
    out['simple_explanation_signals'] = ml['signals']
    out['final_assessment_explanation'] = fa_expl
    return out

@router.post('/verify')
def verify_only(body: PredictIn, user: User = Depends(get_current_user)):
    return verify(body.headline, body.article_content)

@router.get('/predictions')
def history(q: str = Query(default=''), assessment: str = Query(default=''),
            sort: str = Query(default='new'), user: User = Depends(get_current_user),
            db: Session = Depends(get_db)):
    qs = db.query(Prediction).filter(Prediction.user_id == user.id)
    if q:
        like = f'%{q}%'
        qs = qs.filter(or_(Prediction.headline.ilike(like), Prediction.ml_prediction.ilike(like)))
    if assessment:
        qs = qs.filter(Prediction.final_assessment == assessment)
    qs = qs.order_by(desc(Prediction.created_at) if sort != 'old' else asc(Prediction.created_at))
    return [_pred_to_dict(p) for p in qs.limit(200).all()]

@router.get('/predictions/{pid}')
def get_one(pid: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    p = db.query(Prediction).filter(Prediction.id == pid, Prediction.user_id == user.id).first()
    if not p:
        raise HTTPException(status_code=404, detail='Prediction not found.')
    return _pred_to_dict(p)

@router.delete('/predictions/{pid}')
def delete_one(pid: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    p = db.query(Prediction).filter(Prediction.id == pid, Prediction.user_id == user.id).first()
    if not p:
        raise HTTPException(status_code=404, detail='Prediction not found.')
    db.delete(p); db.commit()
    return {'message': 'Deleted.'}

@router.get('/dashboard')
def dashboard(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.query(Prediction).filter(Prediction.user_id == user.id).all()
    total = len(rows)
    fake = sum(1 for r in rows if r.final_assessment == 'LIKELY FAKE')
    real = sum(1 for r in rows if r.final_assessment == 'LIKELY REAL')
    review = sum(1 for r in rows if r.final_assessment == 'NEEDS VERIFICATION')
    recent = sorted(rows, key=lambda r: r.created_at or 0, reverse=True)[:5]
    return {'total': total, 'likely_fake': fake, 'likely_real': real,
            'needs_verification': review, 'recent': [_pred_to_dict(r) for r in recent]}

@router.get('/model-performance')
def model_performance():
    import json, os
    path = 'D:/documents/FNDS/ml/reports/evaluation.json'
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail='Model evaluation report not found.')
    with open(path) as f:
        return json.load(f)
