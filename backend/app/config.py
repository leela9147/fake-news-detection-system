import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql+psycopg2://postgres@127.0.0.1:5432/fndb')
JWT_SECRET = os.getenv('JWT_SECRET', 'dev-secret-change-me')
JWT_EXPIRE_MINUTES = int(os.getenv('JWT_EXPIRE_MINUTES', '60'))
SMTP_HOST = os.getenv('SMTP_HOST', '')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587') or 587)
SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
SMTP_FROM_EMAIL = os.getenv('SMTP_FROM_EMAIL', 'noreply@fnds.local')
FRONTEND_RESET_URL = os.getenv('FRONTEND_RESET_URL', 'http://localhost:5173/reset-password')
WEB_SEARCH_API_KEY = os.getenv('WEB_SEARCH_API_KEY', '')
MODEL_PATH = os.getenv('MODEL_PATH', 'D:/documents/FNDS/ml/models/best_model.joblib')
METADATA_PATH = os.getenv('METADATA_PATH', 'D:/documents/FNDS/ml/models/model_metadata.json')
CONFIDENCE_THRESHOLD = float(os.getenv('CONFIDENCE_THRESHOLD', '0.80'))
