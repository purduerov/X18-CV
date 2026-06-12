import math

LAT_SCALE = 60.0  # 1 degree latitude = 60 NM (always)

def assess_risk(iceberg, platform):
  keel = abs(iceberg['Keel Depth'])
  depth = abs(platform['Depth'])

  heading_radians = math.radians(iceberg['Heading'])
  dx = math.sin(heading_radians)
  dy = math.cos(heading_radians)

  A = dy
  B = -dx
  C = dx * iceberg['y'] - dy * iceberg['x']
  closest_distance = abs(A * platform['x'] + B * platform['y'] + C)

  v_x = platform['x'] - iceberg['x']
  v_y = platform['y'] - iceberg['y']

  dot_product = (v_x * dx) + (v_y * dy)

  if dot_product < 0:
    closest_distance = math.sqrt(v_x**2 + v_y**2)

  if closest_distance <= 5:
    platform_color = 'Red'
  elif closest_distance <= 10:
    platform_color = 'Yellow'
  else:
    platform_color = 'Green'

  if keel >= 1.10 * depth:
    platform_color = 'Green'

  if closest_distance > 25:
    subsea_color = 'Green'
  else:
    if keel >= 1.10 * depth:
      subsea_color = 'Green'
    elif keel >= 0.90 * depth:
      subsea_color = 'Red'
    elif keel >= 0.70 * depth:
      subsea_color = 'Yellow'
    else:
      subsea_color = 'Green'

  return platform_color, subsea_color

def dms_to_decimal(degrees, minutes, seconds, direction):
    # Calculate decimal value
    decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
    
    # Flip to negative if South or West
    if direction.upper() in ['S', 'W']:
        decimal = -decimal
        
    return decimal

# Longitude scale: 1 degree lon = 60 * cos(lat) NM at a given latitude.
# Use the mean latitude of both positions as the reference.
_iceberg_lat = dms_to_decimal(47, 39, 0, 'N')
_platform_lat = 46.7504
LON_SCALE = LAT_SCALE * math.cos(math.radians((_iceberg_lat + _platform_lat) / 2))

iceberg = {
  'x': dms_to_decimal(48, 37, 0, 'W') * LON_SCALE, # Longitude E/W (NM)
  'y': _iceberg_lat * LAT_SCALE,                    # Latitude N/S  (NM)
  'Heading': 158.0,
  'Keel Depth': 99.0
}

platform = {
  'x': -48.7819 * LON_SCALE, # Longitude E/W (NM)
  'y': _platform_lat * LAT_SCALE, # Latitude N/S  (NM)
  'Depth': -78
}

platform_risk, subsea_risk = assess_risk(iceberg, platform)

print(f'Platform risk is ({platform_risk})\nSubsea   risk is ({subsea_risk})')