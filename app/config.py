import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")

    if not SECRET_KEY:
        raise Exception("SECRET_KEY is required")

    DATABASE_URL = os.getenv("DATABASE_URL")

    if not DATABASE_URL:
        raise Exception("DATABASE_URL is required")

    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    RESEND_API_KEY = os.getenv("RESEND_API_KEY")
    MAIL_FROM_EMAIL = os.getenv(
        "MAIL_FROM_EMAIL",
         "notifications@optocare.net"
    )
    MAIL_FROM_NAME = os.getenv(
        "MAIL_FROM_NAME",
        "Optocare"
    )
    FRONTEND_URL = os.getenv(
        "FRONTEND_URL",
        "https://optocare.net"
    )