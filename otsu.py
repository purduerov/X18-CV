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

def otsu_thresh(image_bgr):
    image = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    image = cv2.GaussianBlur(image, (3, 3), 0)
    return cv2.threshold(
        image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU,
    )

def find_rects(image_bgr):
    image_bgr = red_filter(image_bgr)
    raw_contours = image_bgr.copy()

    otsu_threshold, image = otsu_thresh(image_bgr)

    edge = cv2.Canny(image, 0, otsu_threshold)
    
    cv2.imshow("edge", edge)

    contours, _ = cv2.findContours(edge, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    height, width, _ = image_bgr.shape
    raw_contours = np.zeros((height, width)).astype(np.uint8)

    cv2.drawContours(raw_contours, contours, -1, (255, 255, 255), 1)
    cv2.imshow("raw", raw_contours)
    raw_contours = cv2.GaussianBlur(raw_contours, (45, 45), 0)

    _, raw_contours = cv2.threshold(raw_contours, 1, 255, cv2.THRESH_BINARY)

    recontours, _ = cv2.findContours(raw_contours, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    image_copy = image_bgr.copy()

    cv2.polylines(image_copy, pts=recontours, isClosed=False, color=(255, 0, 0), thickness=3)

    polies = [cv2.approxPolyDP(cnt, 100, True) for cnt in recontours]

    cv2.polylines(image_copy, pts=polies, isClosed=True, color=(0, 0, 165), thickness=3)

    polies = [poly for poly in polies if len(poly) == 4]

    cv2.polylines(image_copy, pts=polies, isClosed=True, color=(0, 165, 0), thickness=6)
    
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
