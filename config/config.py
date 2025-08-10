import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Config:
    # SQL Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Secret keys
    SECRET_KEY = os.getenv('SECRET_KEY')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ALGORITHM = 'HS256'  # Default JWT algorithm

    # JWT Configuration
    ACCESS_TOKEN_SECRET_KEY = os.getenv('ACCESS_TOKEN_SECRET_KEY')
    REFRESH_TOKEN_SECRET_KEY = os.getenv('REFRESH_TOKEN_SECRET_KEY')
    

    # Access code for GURU role
    GURU_ACCESS_CODE = os.getenv('GURU_ACCESS_CODE')

    # Access and Refresh Token Keys
    ACCESS_TOKEN_EXPIRES = timedelta(
        minutes=int(os.getenv('ACCESS_TOKEN_EXPIRES_MINUTES', 30))
    )
    REFRESH_TOKEN_EXPIRES = timedelta(
        minutes=int(os.getenv('REFRESH_TOKEN_EXPIRES_MINUTES', 60 * 24 * 7))  # Default to 7 days
    )

    # BaseUrl
    MODULE_BASE_URL = os.getenv('MODULE_BASE_URL')
    GLOBAL_MODULE_URL = os.getenv('GLOBAL_MODULE_URL')
    EXAM_BASE_URL = os.getenv('EXAM_BASE_URL')
 
    