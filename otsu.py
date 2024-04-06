import cv2
import numpy as np 
import matplotlib.pyplot as plt
from pprint import pprint
import math
import time
from ratio import calculate_wh_ratio
from red_filter import red_filter

class RollingAverage:
  def __init__(self, window_size):
    self.window_size = window_size
    self.values = []

  def add(self, value):
    self.values.append(value)
    if len(self.values) > self.window_size:
      self.values.pop(0)

  def get_average(self):
    return sum(self.values) / len(self.values)

def maxl(l): return l.index(max(l))

def find_rects(image_bgr):
    image_bgr = red_filter(image_bgr)
    raw_contours = image_bgr.copy()
    image = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)

    image = cv2.GaussianBlur(image, (3, 3), 0)

    # Set total number of bins in the histogram
    bins_num = 512
    
    # Get the image histogram
    hist, bin_edges = np.histogram(image, bins=bins_num)
    
    # Get normalized histogram if it is required
    # if is_normalized:
    #     hist = np.divide(hist.ravel(), hist.max())
    
    # Calculate centers of bins
    bin_mids = (bin_edges[:-1] + bin_edges[1:]) / 2.
    
    # Iterate over all thresholds (indices) and get the probabilities w1(t), w2(t)
    weight1 = np.cumsum(hist)
    weight2 = np.cumsum(hist[::-1])[::-1]
    
    # Get the class means mu0(t)
    mean1 = np.cumsum(hist * bin_mids) / weight1
    # Get the class means mu1(t)
    mean2 = (np.cumsum((hist * bin_mids)[::-1]) / weight2[::-1])[::-1]
    
    inter_class_variance = weight1[:-1] * weight2[1:] * (mean1[:-1] - mean2[1:]) ** 2
    
    # Maximize the inter_class_variance function val
    index_of_max_val = np.argmax(inter_class_variance)
    
    threshold = bin_mids[:-1][index_of_max_val]
    # print("Otsu's algorithm implementation thresholding result: ", threshold)

    otsu_threshold, image_result = cv2.threshold(
        image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU,
    )
    # print("Obtained threshold: ", otsu_threshold)

    edge = cv2.Canny(image, 0, otsu_threshold)
    
    cv2.imshow("edge", edge)

    contours, _ = cv2.findContours(edge, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # for contour in contours:
    #     image_copy = image_bgr.copy()
    height, width, channels = image_bgr.shape
    raw_contours = np.zeros((height, width)).astype(np.uint8)

    cv2.drawContours(raw_contours, contours, -1, (255, 255, 255), 1)
    cv2.imshow("raw", raw_contours)
    raw_contours = cv2.GaussianBlur(raw_contours, (45, 45), 0)

    ret, raw_contours = cv2.threshold(raw_contours, 1, 255, cv2.THRESH_BINARY)

    recontours, _ = cv2.findContours(raw_contours, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # cnt_largest_i = maxl(list(cv2.contourArea(c) for c in recontours))
    # cnt_largest = recontours[cnt_largest_i]

    image_copy = image_bgr.copy()

    cv2.polylines(image_copy, pts=recontours, isClosed=False, color=(255, 0, 0), thickness=3)

    # epsilon = 0.02 * cv2.arcLength(cnt_largest, True)
    # approx = cv2.approxPolyDP(cnt_largest, epsilon, True)
    # approx = approx[len(approx) - 4:]

    polies = [cv2.approxPolyDP(cnt, 100, True) for cnt in recontours]

    cv2.polylines(image_copy, pts=polies, isClosed=True, color=(0, 0, 165), thickness=3)

    polies = [poly for poly in polies if len(poly) == 4]

    # cv2.polylines(image_copy, pts=polies, isClosed=True, color=(0, 255, 0), thickness=6)
    
    return (image_copy, polies)

def order_points(points):
    # Sort the points based on the y-coordinate (row number)
    sorted_points = sorted(points, key=lambda x: x[1])

    # Separate the points into top and bottom halves
    top_half = sorted_points[:len(sorted_points) // 2]
    bottom_half = sorted_points[len(sorted_points) // 2:]

    # Find the top left and top right points
    top_left = min(top_half, key=lambda x: x[0])
    top_right = max(top_half, key=lambda x: x[0])

    # Find the bottom left and bottom right points
    bottom_left = min(bottom_half, key=lambda x: x[0])
    bottom_right = max(bottom_half, key=lambda x: x[0])

    return [bottom_left, bottom_right, top_left, top_right]

def max_area(rects):
    m_area = -1
    m_rect = []
    for rect in rects:
        if m_area < cv2.contourArea(rect):
            m_area = m_area
            m_rect = rect
    return m_rect

ratio = RollingAverage(60)
prev_x = RollingAverage(60)
prev_y = RollingAverage(60)

# obj_height = 8.5 * 2.54
obj_height = 36

cap = cv2.VideoCapture("data/camera_roll/video1.avi")
# cap = cv2.VideoCapture(1)

while cap.isOpened():
# if True:
    # ret, frame = [True, cv2.imread("data/struct.jpg")]
    ret, frame = cap.read()
    
    if ret:
        image, rects = find_rects(frame)
        
        height, width, channels = image.shape;
        
        rect = max_area(rects)
        # print("\n\n")
        
        if len(rect) != 0:
        # for rect in rects:
            cv2.polylines(image, pts=[rect], isClosed=True, color=(0, 255, 0), thickness=6)
            points = [
                rect[0][0],
                rect[1][0],
                rect[2][0],
                rect[3][0],
            ]
            points = order_points(points)
            print(points)
            prev_x.add(points[0][0])
            prev_y.add(points[0][1])
            
            dist_from_prev = math.sqrt((points[0][0] - prev_x.get_average())**2 + (points[0][1] - prev_y.get_average())**2)
            
            # if dist_from_prev < min(height, width) / 4:
            if True:
                ratio.add(calculate_wh_ratio.get_wh_ratio(
                    points[0],
                    points[1],
                    points[2],
                    points[3],
                    width,
                    height
                ))
                # ratio = (calculate_wh_ratio.get_wh_ratio(
                #     points[0],
                #     points[1],
                #     points[2],
                #     points[3],
                #     width,
                #     height
                # ))
                ratio_avg = ratio.get_average()
                calculated_width = obj_height / ratio_avg
                
                cv2.putText(image, f'ratio: {round(ratio_avg, 3)}\nwidth: {round(calculated_width, 3)}\nerror: {round((abs(55 - calculated_width)), 3)}', tuple(points[2]), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 3, cv2.LINE_AA)
                # cv2.putText(image, f'width: {round(calculated_width, 3)}', (points[2][0], points[2][0] + 4), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3, cv2.LINE_AA)
                # cv2.putText(image, f'error: {round((abs(11.5 * 2.54 - calculated_width)), 3)}', (points[2][0], points[2][0] + 4), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3, cv2.LINE_AA)
        
        cv2.imshow("res", image)
        cv2.waitKey()
    # if cv2.waitKey(1) & 0xFF == ord('q'): 
    #     break

# cap.release()
cv2.destroyAllWindows()
