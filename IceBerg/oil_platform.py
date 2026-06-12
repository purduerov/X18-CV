import math

NAUTICAL_MILE = 60.0

def assess_risk(iceberg, platform):
  iceberg['Keel Depth'] = abs(iceberg['Keel Depth'])
  platform['Depth'] = abs(platform['Depth'])

  heading_radians = math.radians(iceberg['Heading'])
  dx = math.sin(heading_radians)
  dy = math.cos(heading_radians)

  A = dy
  B = -dx
  C = dx * iceberg['y'] - dy * iceberg['x']
  numerator = abs(A * platform['x'] + B * platform['y'] + C)
  denom = math.sqrt(A*A + B*B)

  if denom == 0:
    return "Error"
  
  closest_distance = numerator / denom
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

  if iceberg['Keel Depth'] >= 1.10 * platform['Depth']:
    platform_color = 'Green'

  if closest_distance > 25:
    subsea_color = 'Green'
  else:
    if iceberg['Keel Depth'] >= 1.10 * platform['Depth']:
      subsea_color = 'Green'
    elif iceberg['Keel Depth'] >= 0.90 * platform['Depth']:
      subsea_color = 'Red'
    elif iceberg['Keel Depth'] >= 0.70 * platform['Depth']:
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

iceberg = {
  'x': dms_to_decimal(48, 37, 0, 'W') * NAUTICAL_MILE, # Longitude E/W
  'y': dms_to_decimal(47, 39, 0, 'N') * NAUTICAL_MILE, # Latitude N/S
  'Heading': 158.0,
  'Keel Depth': 99.0
}

platform = {
  'x': -48.7819 * NAUTICAL_MILE, # Longitude E/W
  'y': 46.7504 * NAUTICAL_MILE, # Latitude N/S
  'Depth': -78
}

platform, subsea = assess_risk(iceberg, platform)

print(f'Platform risk is ({platform})\nSubsea   risk is ({subsea})')