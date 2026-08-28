import os
import sqlite3

from flask import current_app, g


def get_db():

    if "db" not in g:

        database_path = current_app.config["DATABASE"]

        os.makedirs(
            os.path.dirname(database_path),
            exist_ok=True
        )

        db = sqlite3.connect(
            database_path
        )

        db.row_factory = sqlite3.Row

        # Enable foreign keys
        db.execute(
            "PRAGMA foreign_keys = ON"
        )

        g.db = db

    return g.db


def close_db(error=None):

    db = g.pop(
        "db",
        None
    )

    if db is not None:
        db.close()


def register_db_teardown(app):

    app.teardown_appcontext(
        close_db
    )


def ensure_db_exists(app):

    database_path = app.config["DATABASE"]

    schema_path = app.config["SCHEMA_FILE"]

    os.makedirs(
        os.path.dirname(database_path),
        exist_ok=True
    )

    # =====================================================
    # CREATE DATABASE IF IT DOES NOT EXIST
    # =====================================================

    if not os.path.exists(database_path):

        if not os.path.exists(schema_path):

            raise FileNotFoundError(
                f"Database schema not found: {schema_path}"
            )

        with open(
            schema_path,
            "r",
            encoding="utf-8"
        ) as f:

            schema = f.read()

        db = sqlite3.connect(
            database_path
        )

        try:

            db.execute(
                "PRAGMA foreign_keys = ON"
            )

            db.executescript(
                schema
            )

            db.commit()

        finally:

            db.close()

    # =====================================================
    # MIGRATE EXISTING DATABASE
    # =====================================================

    db = sqlite3.connect(
        database_path
    )

    try:

        db.execute(
            "PRAGMA foreign_keys = ON"
        )

        # Check whether detections table exists
        table = db.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            AND name = 'detections'
            """
        ).fetchone()

        if table:

            # Get existing columns
            columns = db.execute(
                "PRAGMA table_info(detections)"
            ).fetchall()

            column_names = {
                column[1]
                for column in columns
            }

            # ---------------------------------------------
            # Add decision_reason if missing
            # ---------------------------------------------

            if "decision_reason" not in column_names:

                db.execute(
                    """
                    ALTER TABLE detections
                    ADD COLUMN decision_reason TEXT
                    """
                )

                print(
                    "Database migration: "
                    "decision_reason column added."
                )

        db.commit()

    finally:

        db.close()