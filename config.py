import os


BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:

    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "geo-guard-ai-development-secret-key"
    )

    DATABASE = os.path.join(
        BASE_DIR,
        "database.db"
    )

    UPLOAD_BEFORE = os.path.join(
        BASE_DIR,
        "uploads",
        "before"
    )

    UPLOAD_AFTER = os.path.join(
        BASE_DIR,
        "uploads",
        "after"
    )

    UPLOAD_RESULTS = os.path.join(
        BASE_DIR,
        "uploads",
        "results"
    )

    REPORTS_DIR = os.path.join(
        BASE_DIR,
        "uploads",
        "reports"
    )

    MAX_CONTENT_LENGTH = 50 * 1024 * 1024

    HISTORY_PAGE_SIZE = 10