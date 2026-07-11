import math

def assess_risk(iceberg, platform):
    """
    iceberg:
        {
            "lat": float,
            "lon": float,
            "heading": float,
            "keel_depth": float
        }

    platform:
        {
            "name": str,
            "lat": float,
            "lon": float,
            "water_depth": float
        }
    """

    keel_depth = abs(iceberg["keel_depth"])
    water_depth = abs(platform["water_depth"])

    # --------------------------------------------------
    # Convert platform location into local nautical-mile
    # coordinates relative to iceberg position
    # --------------------------------------------------

    lat_diff = platform["lat"] - iceberg["lat"]
    lon_diff = platform["lon"] - iceberg["lon"]

    y = lat_diff * 60.0

    x = (
        lon_diff
        * 60.0
        * math.cos(math.radians(iceberg["lat"]))
    )

    # --------------------------------------------------
    # Iceberg heading vector
    # 0° = North
    # 90° = East
    # --------------------------------------------------

    heading_rad = math.radians(iceberg["heading"])

    dx = math.sin(heading_rad)
    dy = math.cos(heading_rad)

    # --------------------------------------------------
    # Determine closest approach distance
    # --------------------------------------------------

    dot = x * dx + y * dy

    if dot < 0:
        # Platform is behind iceberg
        closest_distance = math.sqrt(x**2 + y**2)
    else:
        # Perpendicular distance to path
        closest_distance = abs(x * dy - y * dx)

    # --------------------------------------------------
    # Surface platform threat
    # --------------------------------------------------

    if keel_depth >= 1.10 * water_depth:
        platform_threat = "Green"
    else:
        if closest_distance < 5:
            platform_threat = "Red"
        elif closest_distance <= 10:
            platform_threat = "Yellow"
        else:
            platform_threat = "Green"

    # --------------------------------------------------
    # Subsea asset threat
    # --------------------------------------------------

    if closest_distance > 25:
        subsea_threat = "Green"

    elif keel_depth >= 1.10 * water_depth:
        subsea_threat = "Green"

    else:
        ratio = keel_depth / water_depth

        if ratio >= 0.90:
            subsea_threat = "Red"
        elif ratio >= 0.70:
            subsea_threat = "Yellow"
        else:
            subsea_threat = "Green"

    return {
        "Platform": platform["name"],
        "Closest Distance (nm)": round(closest_distance, 2),
        "Platform Threat": platform_threat,
        "Subsea Threat": subsea_threat
    }




# --------------------------------------------------
# Convert DMS to decimal degrees
# --------------------------------------------------

def dms_to_decimal(degrees, minutes, seconds, direction):
    decimal = degrees + minutes/60 + seconds/3600

    if direction in ("S", "W"):
        decimal *= -1

    return decimal

# --------------------------------------------------
# Example iceberg
# --------------------------------------------------

iceberg = {
    "lat": dms_to_decimal(47, 56, 0, "N"),
    "lon": dms_to_decimal(47, 45, 0, "W"),
    "heading": 181,
    "keel_depth": 126
}


# --------------------------------------------------
# MATE oil platforms
# --------------------------------------------------

platforms = [
    {
        "name": "Hibernia",
        "lat": 46.7504 ,
        "lon": -48.7819,
        "water_depth": 78
    },

    {
        "name": "Hebron",
        "lat": 46.544,
        "lon": -48.518,
        "water_depth": 93
    },

    {
        "name": "Sea Rose",
        "lat": 46.7895,
        "lon": -48.146,
        "water_depth": 107
    },
    {
        "name": "Terra Nova",
        "lat": 46.4,
        "lon": -48.4,
        "water_depth": 91
    }
    
]

for platform in platforms:
    result = assess_risk(iceberg, platform)

    print(f"\n{result['Platform']}")
    print(f"Closest Distance: {result['Closest Distance (nm)']} nm")
    print(f"Platform Threat: {result['Platform Threat']}")
    print(f"Subsea Threat: {result['Subsea Threat']}")