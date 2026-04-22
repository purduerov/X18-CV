import cv2 
import numpy as np 
    
frame = cv2.imread("pic.JPG")

# It converts the BGR color space of image to HSV color space 
hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV) 
imgray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
ret, thresh = cv2.threshold(imgray, 127, 255, 0)

gaussian = cv2.adaptiveThreshold(imgray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,11,2)


cv2.imshow("Grayscale", thresh)
cv2.imshow("Gaussian", gaussian)
cv2.waitKey(0) 
cv2.destroyAllWindows()