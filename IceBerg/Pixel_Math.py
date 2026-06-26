import math

def rotate_point_around_z(point, pivot, theta):
    # Convert angle to radians
    cos_theta = math.cos(theta)
    sin_theta = math.sin(theta)
    
    # Unpack 3D coordinates (X=side, Y=up, Z=depth)
    x, y, z = point
    cx, cy, cz = pivot
    
    # 1. Translate point so pivot is at origin (Y and Z only)
    ty = y - cy
    tz = z - cz
    
    # 2. Apply rotation to Y and Z
    # Standard right-handed rotation around Y:
    new_y = (ty * cos_theta) + (-tz * sin_theta)
    new_z = (ty * sin_theta) + (tz * cos_theta)
    
    # 3. Translate back, X remains the same
    return (x, new_y + cy, new_z + cz)

def rotate_point_around_y(point, pivot, theta):
    # Convert angle to radians
    cos_theta = math.cos(theta)
    sin_theta = math.sin(theta)
    
    # Unpack 3D coordinates (X=side, Y=up, Z=depth)
    x, y, z = point
    cx, cy, cz = pivot
    
    # 1. Translate point so pivot is at origin (X and Z only)
    tx = x - cx
    tz = z - cz
    
    # 2. Apply rotation to X and Z
    # Standard right-handed rotation around Y:
    new_x = (tx * cos_theta) + (tz * sin_theta)
    new_z = (-tx * sin_theta) + (tz * cos_theta)
    
    # 3. Translate back, Y remains the same
    return (new_x + cx, y, new_z + cz)

def get_rel_points(p, c):
    new_point = [p[i] - c[i] for i in range(3)]
    return new_point

def get_coords(matrix):
    if matrix[2] == 0:
        return 0, 0
    fx = 284.6772155761719 
    fy = 284.5019836425781 
    cx = 318.91168212890625 
    cy = 198.20179748535156
    new_x = matrix[0] * fx + matrix[2] * cx
    new_y = matrix[1] * fy + matrix[2] * cy
    new_x /= matrix[2]
    new_y /= matrix[2]
    return new_x, new_y

def produce_coords(coord, pivot, angle):
    rotated = rotate_point_around_y(coord, pivot, angle)
    return get_coords(rotated)

def calc_length(X_height, known_length, var_length):
    hypo = 3.44 * X_height
    if abs((known_length / X_height) - 3.44) < 0.1:
        print((var_length / X_height) * 15)
        return
    X_depth = math.sqrt(hypo**2 - known_length**2)
    top_x = get_coords((0, 0, X_depth))
    bottom_x = get_coords((0, X_height, X_depth))
    pivot = (0, 0, X_depth)

    angle = math.acos(known_length / hypo)
    new_point = (known_length, var_length, 0)
    
    top_var = produce_coords(new_point, pivot, -angle)
    new_point = (known_length, 0, 0)
    bottom_var = produce_coords(new_point, pivot, -angle)
    known_height = abs(top_x[1] - bottom_x[1])
    var_height = abs(top_var[1] - bottom_var[1])
    ratio = var_height / known_height
    print(f'Predicted Height is {ratio * 15}')
    # print(top_x)
    # print(bottom_x)
    # print(top_var)
    # print(bottom_var)
    
calc_length(82.02438661763951, 287.69602013236124, 355.27594908746636)

def test():
    p = (1, 1, 1)
    c = (2, 0, 0)
    del_z = p[2] - c[2]
    del_x = p[0] - c[0]
    angle = math.atan2(del_z, del_x)
    # print(f"Aligned Point: {align_to_y_level(p, c)}")
    print(rotate_point_around_y(p, c, -angle + math.pi /2))
