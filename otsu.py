import cv2
import numpy as np 
import matplotlib.pyplot as plt
from pprint import pprint
import time

def maxl(l): return l.index(max(l))

def find_rects(image_bgr):
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
    print("Otsu's algorithm implementation thresholding result: ", threshold)

    otsu_threshold, image_result = cv2.threshold(
        image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU,
    )
    print("Obtained threshold: ", otsu_threshold)

    edge = cv2.Canny(image, 0, otsu_threshold)

    contours, _ = cv2.findContours(edge, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # for contour in contours:
    #     image_copy = image_bgr.copy()
    height, width, channels = image_bgr.shape
    raw_contours = np.zeros((height, width)).astype(np.uint8)

    cv2.drawContours(raw_contours, contours, -1, (255, 255, 255), 2)
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

    cv2.polylines(image_copy, pts=polies, isClosed=True, color=(0, 255, 0), thickness=6)
    
    return (image_copy, polies)

cap = cv2.VideoCapture("data/camera_roll/video1.avi")
# cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    
    if ret:
        image, corners = find_rects(frame)
        
        cv2.imshow("res", image)
        time.sleep(0.1)
        
    if cv2.waitKey(1) & 0xFF == ord('q'): 
        break

cap.release()
cv2.destroyAllWindows()
