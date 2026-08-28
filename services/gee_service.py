import ee


PROJECT_ID = "geoguard-ai-506914"


def initialize_gee():
    """Initialize Google Earth Engine."""
    try:
        ee.Initialize(project=PROJECT_ID)
        return True
    except Exception as e:
        print(f"GEE initialization error: {e}")
        return False


def get_sentinel2_collection(
    latitude,
    longitude,
    start_date,
    end_date,
    cloud_percentage=20
):
    """
    Search Sentinel-2 imagery for a given location and date range.
    """

    if not initialize_gee():
        raise RuntimeError("Google Earth Engine initialization failed.")

    # Earth Engine uses [longitude, latitude]
    point = ee.Geometry.Point([longitude, latitude])

    # 500 metre area around the selected location
    region = point.buffer(500).bounds()

    # Sentinel-2 Surface Reflectance
    collection = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(region)
        .filterDate(start_date, end_date)
        .filter(
            ee.Filter.lte(
                "CLOUDY_PIXEL_PERCENTAGE",
                cloud_percentage
            )
        )
        .sort("CLOUDY_PIXEL_PERCENTAGE")
    )

    return collection


if __name__ == "__main__":

    print("Testing Google Earth Engine...")

    collection = get_sentinel2_collection(
        latitude=15.123,
        longitude=75.456,
        start_date="2024-01-01",
        end_date="2024-01-31",
        cloud_percentage=20
    )

    number_of_images = collection.size().getInfo()

    print("Number of Sentinel-2 images:", number_of_images)
    print("GEE Sentinel-2 search successful!")