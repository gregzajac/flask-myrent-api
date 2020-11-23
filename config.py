import os
from pathlib import Path
from dotenv import load_dotenv


base_dir = Path(__file__).resolve().parent
env_file = base_dir / '.env'
load_dotenv(env_file)


class Config:
    VERSION = 'v1'
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = ''
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_EXPIRED_MINUTES = 30
    PER_PAGE = 5
    CORS_HEADERS = 'Content-Type'
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024
    UPLOAD_FOLDER = ''


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    UPLOAD_FOLDER = base_dir / 'uploads'


class TestingConfig(Config):
    DB_FILE_PATH = base_dir / 'tests' / 'test.db'
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_FILE_PATH}'
    DEBUG = True
    TESTING = True
    UPLOAD_FOLDER = base_dir / 'tests' / 'uploads'


class ProductionConfig(Config):
    # DB_HOST = os.environ.get('DB_HOST')
    # DB_USERNAME = os.environ.get('DB_USERNAME')
    # DB_PASSWORD = os.environ.get('DB_PASSWORD')
    # DB_NAME = os.environ.get('DB_NAME')
    # SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}?charset=utf8mb4'
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    UPLOAD_FOLDER = base_dir / 'uploads'


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}