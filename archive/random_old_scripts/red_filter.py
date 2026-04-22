import numpy as np

def red_filter(image):
    b, g, r = np.int64(image[:, :, 0]), np.int64(image[:, :, 1]), np.int64(image[:, :, 2])

    mask = (r - b > 30) & (r - g > 30)

    image[mask] = np.array([r[mask], r[mask], r[mask]]).transpose().astype(np.uint8)

    return image