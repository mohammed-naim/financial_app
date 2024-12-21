# Config
import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()


class Config:
    FLASK_APP = os.getenv('FLASK_APP')
    FLASK_ENV = os.getenv('FLASK_ENV')
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = True if os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS').lower() == 'true' else False
    LOGIN_DISABLED = True if os.getenv('LOGIN_DISABLED').lower() == 'true' else False
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=60)
    # have session and remember cookie be samesite (flask/flask_login)
    REMEMBER_COOKIE_SAMESITE = "strict"
    SESSION_COOKIE_SAMESITE = "strict"
