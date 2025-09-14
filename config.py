import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI", "postgresql+psycopg2://Securepy:mynewpass@localhost:5433/securepy_database")
    #SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///securepy.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    DP_EPSILON = float(os.getenv("DP_EPSILON", "1.0"))

class DevConfig(Config):
    DEBUG = True

class ProdConfig(Config):
    DEBUG = False
