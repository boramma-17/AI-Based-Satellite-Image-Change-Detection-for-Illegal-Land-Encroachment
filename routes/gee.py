from flask import Blueprint, render_template, request

from services.gee_service import search_sentinel2


gee_bp = Blueprint(
    "gee",
    __name__,
    url_prefix="/gee"
)


@gee_bp.route("/search", methods=["GET", "POST"])
def search():

    result = None
    error = None

    if request.method == "POST":

        try:
            latitude = float(request.form["latitude"])
            longitude = float(request.form["longitude"])

            start_date = request.form["start_date"]
            end_date = request.form["end_date"]

            cloud_percentage = int(
                request.form.get("cloud_percentage", 20)
            )

            result = search_sentinel2(
                latitude,
                longitude,
                start_date,
                end_date,
                cloud_percentage
            )

        except Exception as e:
            error = str(e)

    return render_template(
        "gee_search.html",
        result=result,
        error=error
    )