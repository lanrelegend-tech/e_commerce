from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Config:
    SECRET_KEY = "your-secret-key"
    JWT_SECRET_KEY = "your-jwt-secret-key"

    SQLALCHEMY_DATABASE_URI = f"sqlite:///{BASE_DIR / 'instance' / 'ecommerce.db'}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False