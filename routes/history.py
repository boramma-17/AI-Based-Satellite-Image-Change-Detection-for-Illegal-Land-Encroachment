from flask import (
    Blueprint,
    render_template,
    request,
    session,
    current_app,
)

from utils.helpers import login_required
from utils.database import get_db
from services.map_service import build_detections_map


# IMPORTANT:
# This must be "history", NOT "detection".
bp = Blueprint("history", __name__)


# =========================================================
# Detection History
# =========================================================

@bp.route("/history")
@login_required
def history():

    db = get_db()

    page = max(
        1,
        request.args.get(
            "page",
            1,
            type=int
        )
    )

    page_size = current_app.config.get(
        "HISTORY_PAGE_SIZE",
        10
    )

    offset = (page - 1) * page_size

    # -----------------------------------------------------
    # Count user's detections
    # -----------------------------------------------------

    total = db.execute(
        """
        SELECT COUNT(*) AS c
        FROM detections
        WHERE user_id = ?
        """,
        (
            session["user_id"],
        ),
    ).fetchone()["c"]

    # -----------------------------------------------------
    # Get user's detections
    # -----------------------------------------------------

    detections = db.execute(
        """
        SELECT *
        FROM detections
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?
        """,
        (
            session["user_id"],
            page_size,
            offset,
        ),
    ).fetchall()

    has_next = (
        offset + page_size < total
    )

    has_prev = page > 1

    return render_template(
        "history.html",
        detections=detections,
        page=page,
        has_next=has_next,
        has_prev=has_prev,
    )


# =========================================================
# Detection Map
# =========================================================

@bp.route("/map")
@login_required
def map_view():

    db = get_db()

    detections = db.execute(
        """
        SELECT *
        FROM detections
        WHERE user_id = ?
        ORDER BY created_at DESC
        """,
        (
            session["user_id"],
        ),
    ).fetchall()

    map_html = build_detections_map(
        detections
    )

    return render_template(
        "map.html",
        map_html=map_html,
    )