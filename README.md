# Fake News Detection and Real-World Verification System

A full-stack AI/ML web application. Users sign up, paste a news headline and article,
receive an ML classification with explainable-AI reasoning, a real-world web verification
layer, and a final combined assessment (LIKELY REAL / LIKELY FAKE / NEEDS VERIFICATION).

## Stack

- **Frontend:** React (Vite), react-router-dom, responsive CSS, dark/light mode
- **Backend:** Python, FastAPI, SQLAlchemy, Alembic
- **Database:** PostgreSQL
- **Auth:** JWT (PyJWT), Argon2 password hashing, expiring single-use reset tokens
- **ML:** scikit-learn TF-IDF (1–2 grams) + Logistic Regression / LinearSVC (calibrated) / RandomForest
- **Verification:** Bing HTML search + robots.txt-aware page extraction (BeautifulSoup), cached & rate-limited

## Project layout

```
backend/            FastAPI app, routes, models, verification, ML service
  migrations/       Alembic migrations
  .env.example      Environment template
frontend/           React (Vite) SPA
ml/                 Dataset analysis, training & evaluation scripts
  models/           best_model.joblib + model_metadata.json
  reports/          evaluation.json, error analysis CSVs
data/               raw datasets + processed artifacts
scripts/            Misc helper/smoke scripts
tests/              API test script
```

## Setup

1. **PostgreSQL:** create a database `fndb` and set `DATABASE_URL` accordingly.
2. **Backend:**
   ```bash
   pip install -r backend/requirements.txt
   copy backend\.env.example backend\.env   # then edit values
   cd backend && alembic upgrade head
   uvicorn app.main:app --port 8000
   ```
3. **Train (already done, artifacts committed):**
   ```bash
   python ml/dataset_analysis.py
   python ml/train.py
   ```
4. **Frontend:**
   ```bash
   cd frontend
   npm install
   npm run dev   # http://127.0.0.1:5173
   ```

## Notes / limitations

- The ML model learns patterns from its training data; it is not absolute truth.
- If confidence < 0.80 (justified via validation sweep), the system answers NEEDS VERIFICATION.
- Web verification uses public search results; failures yield "could not be completed", never fabricated evidence.
- For local password reset, the reset URL is printed to the backend console when SMTP is not configured.
