import cv2
import numpy as np

def maxl(l): return l.index(max(l))
 
# Read the original image
img = cv2.imread('data/camera_roll/image10.jpg') 
# Display original image
cv2.imshow('Original', img)
cv2.waitKey(0)
 
# Convert to graycsale
img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# Blur the image for better edge detection
img_blur =  img_gray #cv2.GaussianBlur(img_gray, (3,3), 0) 

# img_blur = cv2.GaussianBlur(img_gray, (35, 35), 0)
# img_blur = cv2.medianBlur(img_gray, 35)

cv2.imshow('blur', img_blur)
cv2.waitKey(0)
 
# Sobel Edge Detection
sobelx = cv2.Sobel(src=img_blur, ddepth=cv2.CV_64F, dx=1, dy=0, ksize=5) # Sobel Edge Detection on the X axis
sobely = cv2.Sobel(src=img_blur, ddepth=cv2.CV_64F, dx=0, dy=1, ksize=5) # Sobel Edge Detection on the Y axis
sobelxy = cv2.Sobel(src=img_blur, ddepth=cv2.CV_64F, dx=1, dy=1, ksize=5) # Combined X and Y Sobel Edge Detection
# Display Sobel Edge Detection Images
grad = np.sqrt(sobelx**2 + sobely**2)
grad_norm = (grad * 255 / grad.max()).astype(np.uint8)

cv2.imshow('Sobel X', sobelx)
cv2.waitKey(0)
cv2.imshow('Sobel Y', sobely)
cv2.waitKey(0)
cv2.imshow('Sobel X Y using Sobel() function', sobelxy)
cv2.waitKey(0)
cv2.imshow('Edges', grad_norm)
cv2.waitKey(0)

edges = cv2.Canny(image=img_blur, threshold1=100, threshold2=200) # Canny Edge Detection
# Display Canny Edge Detection Image
cv2.imshow('Canny Edge Detection', edges)
cv2.waitKey(0)

kernel = np.ones((1,150), np.uint8)  # note this is a horizontal kernel
dilated = cv2.dilate(edges, kernel, iterations=1)
eroded = cv2.erode(dilated, kernel, iterations=1) 

kernel = np.ones((101,101),np.uint8)#cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(10,10))
res = cv2.morphologyEx(eroded,cv2.MORPH_CLOSE,kernel)

cv2.imshow("morph", res)
cv2.waitKey()

notted = cv2.bitwise_not(res)
cv2.imshow('notted', notted)
cv2.waitKey(0)

contours, hierarchy = cv2.findContours(res, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
cnt_largest_i = maxl(list(cv2.contourArea(c) for c in contours))
cnt_largest = contours[cnt_largest_i]

cv2.polylines(img, pts=[cnt_largest], isClosed=False, color=(255, 0, 0), thickness=3)

epsilon = 0.02 * cv2.arcLength(cnt_largest, True)
approx = cv2.approxPolyDP(cnt_largest, epsilon, True)

cv2.polylines(img, pts=[approx], isClosed=False, color=(0, 255, 0), thickness=6)

print(approx)

cv2.imshow('img', img)
# cv2.waitKey(0)

cv2.waitKey()

cv2.destroyAllWindows()