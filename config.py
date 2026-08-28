import os


# Project root directory
BASE_DIR = os.path.abspath(
    os.path.dirname(__file__)
)


class Config:

    # Flask secret key
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "geo-guard-ai-development-secret-key"
    )

    # ==============================
    # DATABASE
    # ==============================

    DATABASE_DIR = os.path.join(
        BASE_DIR,
        "database"
    )

    DATABASE = os.path.join(
        DATABASE_DIR,
        "database.db"
    )

    SCHEMA_FILE = os.path.join(
        DATABASE_DIR,
        "schema.sql"
    )

    # ==============================
    # UPLOAD DIRECTORIES
    # ==============================

    UPLOAD_DIR = os.path.join(
        BASE_DIR,
        "uploads"
    )

    UPLOAD_BEFORE = os.path.join(
        UPLOAD_DIR,
        "before"
    )

    UPLOAD_AFTER = os.path.join(
        UPLOAD_DIR,
        "after"
    )

    UPLOAD_RESULTS = os.path.join(
        UPLOAD_DIR,
        "results"
    )

    REPORTS_DIR = os.path.join(
        UPLOAD_DIR,
        "reports"
    )

    # ==============================
    # FILE SETTINGS
    # ==============================

    MAX_CONTENT_LENGTH = 50 * 1024 * 1024

    # ==============================
    # HISTORY
    # ==============================

    HISTORY_PAGE_SIZE = 10