from flask import Blueprint, jsonify, render_template, session
from utils.database import get_db
from utils.helpers import login_required

bp = Blueprint("history", __name__, url_prefix="/history")

@bp.route("/")
@login_required
def history():
    db = get_db()
    records = db.execute(
        """
        SELECT * FROM detections 
        WHERE user_id = ? 
        ORDER BY created_at DESC
        """,
        (session["user_id"],)
    ).fetchall()
    return render_template("history.html", records=records)

@bp.route("/map")
@login_required
def map_view():
    return render_template("map.html")

@bp.route("/api/live")
@login_required
def get_live_detections():
    db = get_db()
    
    # Safe query using COALESCE to guarantee valid non-null coordinates
    query = """
        SELECT 
            id, 
            COALESCE(latitude, 12.9716) AS lat, 
            COALESCE(longitude, 77.5946) AS lng, 
            COALESCE(location_name, 'Monitored Sector') AS site, 
            COALESCE(land_type, 'Unclassified') AS land_type, 
            CASE WHEN encroachment_flag = 1 THEN 'Illegal' ELSE 'Legal' END AS status,
            COALESCE(area_sqm, 0.0) AS area_sqm, 
            created_at AS timestamp
        FROM detections
    """
    
    if session.get("role") == "admin":
        rows = db.execute(query + " ORDER BY created_at DESC LIMIT 50").fetchall()
    else:
        rows = db.execute(
            query + " WHERE user_id = ? ORDER BY created_at DESC LIMIT 50", 
            (session["user_id"],)
        ).fetchall()

    data = [dict(row) for row in rows]
    
    # Fallback seed pins if user hasn't run detections yet
    if not data:
        data = [
            {
                "id": "GEO-101",
                "lat": 12.9780,
                "lng": 77.5910,
                "site": "Sector 4 Reserve Forest",
                "land_type": "Forest",
                "status": "Illegal",
                "area_sqm": 4200.0,
                "timestamp": "2026-08-25 15:45:00"
            },
            {
                "id": "GEO-102",
                "lat": 12.9620,
                "lng": 77.6100,
                "site": "Wetland Catchment Basin",
                "land_type": "Water Body",
                "status": "Illegal",
                "area_sqm": 1850.0,
                "timestamp": "2026-08-25 15:52:10"
            },
            {
                "id": "GEO-103",
                "lat": 12.9350,
                "lng": 77.5350,
                "site": "Approved Industrial Zone",
                "land_type": "Open Land",
                "status": "Legal",
                "area_sqm": 6100.0,
                "timestamp": "2026-08-25 16:01:45"
            }
        ]
        
    return jsonify({"status": "success", "count": len(data), "data": data})