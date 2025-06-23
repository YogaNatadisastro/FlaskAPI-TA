import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Config:
    # SQL Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Secret keys
    SECRET_KEY = os.getenv('SECRET_KEY', 'defaultsecret')

    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    REFRESH_TOKEN_SECRET_KEY = os.getenv('REFRESH_TOKEN_SECRET_KEY', 15)
    ACCESS_TOKEN_SECRET_KEY = os.getenv('ACCESS_TOKEN_SECRET_KEY', 10080)

    # Access code for GURU role
    GURU_ACCESS_CODE = os.getenv('GURU_ACCESS_CODE')

    # Access and Refresh Token Keys
    ACCESS_TOKEN_EXPIRES = os.getenv('ACCESS_TOKEN_EXPIRES')  
    REFRESH_TOKEN_EXPIRES = os.getenv('REFRESH_TOKEN_EXPIRES')

    # Token Expiry
    ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
    REFRESH_TOKEN_EXPIRES = timedelta(days=7)

    # BaseUrl
    MODULE_BASE_URL = os.getenv('MODULE_BASE_URL')
 
    