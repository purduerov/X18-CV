import numpy as np
import cv2

import CameraStream as rs
#Confirguration for Moving Average

# Configure pipeline
import sys
# 1. Standard Preprocessing
img = cv2.imread('IceBerg.jpeg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# 2. DELETE VERTICAL LINES (The Secret Weapon)
# Create a kernel that is 50 pixels wide and only 1 pixel tall
horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (50, 1))

# Apply morphology: This removes any structure that isn't at least 50px wide
# This will effectively delete the vertical icicles and "bleed"
detected_lines = cv2.morphologyEx(gray, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)

# 3. Edge Detection on the "Cleaned" horizontal image
edges = cv2.Canny(detected_lines, 50, 150, apertureSize=3)

# 4. Hough Lines with Angle Filtering
# In cv2.HoughLines, the theta parameter (pi/2) targets horizontal lines.
# We will filter the results to only keep lines where theta is approx 90 degrees.
lines = cv2.HoughLines(edges, 1, np.pi/180, 150)

waterline_y = None

if lines is not None:
    for rho, theta in lines[0]:
        # Theta for a horizontal line is roughly pi/2 (1.57 radians)
        # We only accept lines between 80 and 100 degrees
        if 1.4 < theta < 1.7:
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a * rho
            y0 = b * rho
            waterline_y = int(y0) # This is the Y-coordinate of your surface
            
            # Draw the line to verify
            cv2.line(img, (0, waterline_y), (img.shape[1], waterline_y), (0, 0, 255), 2)

cv2.imshow('Waterline Found', img)
cv2.waitKey(0)
exit(0)
def display_image(image_path):
    """
    Opens an image file from the given path and displays it in a window.

    Args:
        image_path (str): The full path to the image file.
    """
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray,50,150,apertureSize = 3)
    cv2.imwrite('houghlines3.jpg',edges)
    exit(0)
    lines = cv2.HoughLines(edges,1,np.pi/90,200)
    for rho,theta in lines[0]:
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a*rho
        y0 = b*rho
        x1 = int(x0 + 1000*(-b))
        y1 = int(y0 + 1000*(a))
        x2 = int(x0 - 1000*(-b))
        y2 = int(y0 - 1000*(a))

        cv2.line(img,(x1,y1),(x2,y2),(0,0,255),2)

    cv2.imwrite('houghlines3.jpg',img)


image_file_path = 'IceBerg.jpg' 

# Call the function to run the process
display_image(image_file_path)
exit(0)
# Start streaming
pipeline.start(config)

def dist(p1, p2):
    return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[2]) ** 2) ** 0.5

try:
    label = -1
    while True:
        # Wait for a new frame
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        depth_frame = frames.get_depth_frame()
        if not color_frame:
            continue
        if not depth_frame:
            continue
        # Convert to numpy array
        color_image = np.asanyarray(color_frame.get_data())
        # cv2.imshow("Smoothed Edges with Red Contours", color_image)
        # print("running")
        # continue
        # Convert to grayscale
        gray = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)


        # Apply Gaussian blur to grayscale image
        blurred = cv2.GaussianBlur(gray, (7, 7), 2)

        # Apply Canny edge detection (this gives you the "line video")
        edges = cv2.Canny(blurred, 100, 200)

        # Convert edges to BGR so we can draw red contours on it
        edges_bgr = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

        # Find corners
        corners = cv2.goodFeaturesToTrack(gray, maxCorners=100, qualityLevel = 0.01, minDistance = 10)
        
        true_corners = []
        num_labels, labels = cv2.connectedComponents(edges)

        # Get intrinsics
        depth_intrin = depth_frame.profile.as_video_stream_profile().intrinsics
        c1 = []
        if corners is not None:
            corners = np.int0(corners)
            
            # Filter Corners that lie on edges
            for corner in corners:
                x, y = corner.ravel()
                if edges[int(y), int(x)] > 0:
                    true_corners.append((x, y, labels[y, x]))
                    if len(c1) == 0  :
                        c1.append([x, y, labels[y, x]])
                        # cv2.circle(edges_bgr, (x, y), 3, (0, 0, 255), -1) # Draw Each True Corner
                        continue
                    elif labels[y, x] == c1[0][2]:
                        if label == -1:
                            label = labels[y,x]
                        c1.append([x,y,labels[y,x]])
                        # cv2.circle(edges_bgr, (x, y), 3, (0, 0, 255), -1) # Draw Each True Corner
                    continue
                    cv2.circle(edges_bgr, (x, y), 3, (0, 0, 255), -1) # Draw Each True Corner
                    if depth_frame:
                        depth = depth_frame.get_distance(x,y)
                        point_3d = rs.rs2_deproject_pixel_to_point(depth_intrin, [x, y], depth)
                        X, Y, Z = point_3d
                    #     if depth != 0:
                    #         print(X, Y, Z)
                    # break
            if len(c1) < 2:
                continue
            corner_pair = [-1,-1,-1]
            for i in range(len(c1)):
                for j in range(len(c1)):
                    if i == j:
                        continue
                    if corner_pair[-1] == -1 or corner_pair[-1] < dist(c1[i], c1[j]):
                        corner_pair[0] = c1[i]
                        corner_pair[1] = c1[j]
                        corner_pair[2] = dist(c1[i], c1[j])
            # print(corner_pair)
            points = []
            for i, corner in enumerate(corner_pair):
                if i == 2:
                    continue
                if len(corner_pair) > 1:
                    x = corner[0]
                    y = corner[1]
                    depth = depth_frame.get_distance(x,y)
                    point_3d = rs.rs2_deproject_pixel_to_point(depth_intrin, [x, y], depth)
                    X, Y, Z = point_3d
                    points.append([X, Y, Z])
                cv2.circle(color_image, (corner[0], corner[1]), 3, (0, 0, 255), -1) # Draw Each True Corner
            # print(len(c1))
            if len(points) != 0:
                print(((points[0][0] - points[1][0]) ** 2 + (points[0][1] - points[1][1]) ** 2 + (points[0][2] - points[1][2]) ** 2)**0.5)
        # Show the final image
        cv2.imshow("Smoothed Edges with Red Contours", color_image)

        # Exit on ESC key
        if cv2.waitKey(1) & 0xFF == 27:
            break

finally:
    pipeline.stop()
    cv2.destroyAllWindows()