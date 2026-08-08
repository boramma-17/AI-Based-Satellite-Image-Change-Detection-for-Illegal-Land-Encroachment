import os
import sqlite3

from flask import g, current_app


def get_db():
    if "db" not in g:

        database_path = current_app.config["DATABASE"]

        os.makedirs(
            os.path.dirname(database_path),
            exist_ok=True
        )

        g.db = sqlite3.connect(database_path)

        g.db.row_factory = sqlite3.Row

        # Enable foreign keys
        g.db.execute("PRAGMA foreign_keys = ON")

    return g.db


def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()


def register_db_teardown(app):
    app.teardown_appcontext(close_db)


def ensure_db_exists(app):

    database_path = app.config["DATABASE"]

    # If database doesn't exist, create it from schema.sql
    if not os.path.exists(database_path):

        with app.app_context():

            db = get_db()

            schema_path = os.path.join(
                app.root_path,
                "schema.sql"
            )

            with open(
                schema_path,
                "r",
                encoding="utf-8"
            ) as f:

                schema = f.read()

            db.executescript(schema)

            db.commit()

            return

    # Make sure required tables exist
    with app.app_context():

        db = get_db()

        tables = db.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type='table'
            """
        ).fetchall()

        table_names = {
            row["name"]
            for row in tables
        }

        if "users" not in table_names or "detections" not in table_names:

            schema_path = os.path.join(
                app.root_path,
                "schema.sql"
            )

            with open(
                schema_path,
                "r",
                encoding="utf-8"
            ) as f:

                schema = f.read()

            db.executescript(schema)

            db.commit()