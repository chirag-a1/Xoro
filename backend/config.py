# backend/config.py

import os
from datetime import timedelta

# Get the base directory of the project
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """
    Base configuration settings for the Flask application.
    """
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 
                                             'sqlite:///' + os.path.join(basedir, 'instance', 'trading.db'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=12)
    
    # External APIs
    API_KEY_MARKET_DATA = os.environ.get('API_KEY_MARKET_DATA', 'FR7QX34IT28RQY7A')
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'AIzaSyCw66WcK4xHukuVNAMmVlqdMBWNBo93DxY')
    
    # Development settings
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    
    def __init__(self):
        if not self.SECRET_KEY:
            raise ValueError("SECRET_KEY environment variable must be set in production")
        if not self.JWT_SECRET_KEY:
            raise ValueError("JWT_SECRET_KEY environment variable must be set in production")

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False