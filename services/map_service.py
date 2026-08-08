"""Builds an interactive Folium map of geotagged detections."""
import folium


def build_detections_map(detections, default_center=(20.5937, 78.9629), zoom_start=5):
    """
    detections: iterable of dicts/rows with latitude, longitude, title,
    change_percent, encroachment_flag, created_at.
    Rows without coordinates are skipped.
    """
    geo_points = [d for d in detections if d["latitude"] is not None and d["longitude"] is not None]

    if geo_points:
        center = (geo_points[0]["latitude"], geo_points[0]["longitude"])
    else:
        center = default_center

    fmap = folium.Map(location=center, zoom_start=zoom_start, tiles="OpenStreetMap")

    for d in geo_points:
        color = "red" if d["encroachment_flag"] else "green"
        popup_html = (
            f"<b>{d['title'] or 'Untitled'}</b><br>"
            f"Change: {d['change_percent']}%<br>"
            f"Date: {d['created_at']}"
        )
        folium.Marker(
            location=(d["latitude"], d["longitude"]),
            popup=folium.Popup(popup_html, max_width=250),
            icon=folium.Icon(color=color, icon="warning-sign" if d["encroachment_flag"] else "ok-sign"),
        ).add_to(fmap)

    return fmap._repr_html_()