import cv2
import numpy as np

# Import the image
# cap = cv2.VideoCapture(0)

def undistort(img):
    ret = 2.2063746245104525
    mtx = np.array([
        [1.09530534e+03, 0.00000000e+00, 9.54353075e+02],
        [0.00000000e+00, 1.09011353e+03, 5.41983054e+02],
        [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]
    ])
    dist = np.array([[-0.32290118, 0.09774828, 0.01101426, 0.00701455, -0.01189179]])

    h,  w = img.shape[:2]
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))
    
    mapx, mapy = cv2.initUndistortRectifyMap(mtx, dist, None, newcameramtx, (w,h), 5)
    dst = cv2.remap(img, mapx, mapy, cv2.INTER_LINEAR)
    # crop the image
    x, y, w, h = roi
    x = x + 50
    y = y + 50
    w = w - 50
    h = h - 50
    dst = dst[y:y+h, x:x+w]
    
    return dst

# while cap.isOpened():
#     ret, frame = cap.read()
    
#     if ret:
#         frame = undistort(frame)
#         if cv2.waitKey(1) & 0xFF == ord('s'): 
#             image = frame
#             break
            
#         cv2.imshow("Capture", frame)
        
#     if cv2.waitKey(1) & 0xFF == ord('q'): 
#         break

# # Display the image


# image = cv2.imread('data/camera_roll/image14.jpg')
# image = cv2.imread('data/camera_roll/image14.jpg')
image = cv2.imread('data/struct.jpg')

cv2.imshow('Image', image)
# cv2.imwrite("image.jpeg", image)

pts = []
# Define a mouse callback function
def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        cv2.circle(image,(x,y),10,(255,0,0),-1)
        pts.append((x, y))
        print('Left mouse button clicked at coordinates:', x, y)
        cv2.imshow('Image', image)
        

# Set the mouse callback function
cv2.setMouseCallback('Image', mouse_callback)

# Wait for a key press
cv2.waitKey(0)

# Close the window
cv2.destroyAllWindows()

# in case it matters: licensed under GPLv2 or later
# legend:
# sqr(x)  = x*x
# sqrt(x) = square root of x

# let m1x,m1y ... m4x,m4y be the (x,y) pixel coordinates
# of the 4 corners of the detected quadrangle
# i.e. (m1x, m1y) are the cordinates of the first corner, 
# (m2x, m2y) of the second corner and so on.
# let u0, v0 be the pixel coordinates of the principal point of the image
# for a normal camera this will be the center of the image, 
# i.e. u0=IMAGEWIDTH/2; v0 =IMAGEHEIGHT/2
# This assumption does not hold if the image has been cropped asymmetrically

# first, transform the image so the principal point is at (0,0)
# this makes the following equations much easier
import math
def sqrt(x):
    return math.sqrt(abs(x))
    
def sqr(x):
    return x**2

# m1x = 1110 - u0;
# m1y = 918 - v0;
# m2x = 1701 - u0;
# m2y = 481 - v0;
# m3x = 333 - u0;
# m3y = 316 - v0;
# m4x = 909 - u0;
# m4y = 70 - v0;

# m1x = 751 - u0;
# m1y = 657 - v0;
# m2x = 1423 - u0;
# m2y = 1036 - v0;
# m3x = 922 - u0;
# m3y = 47 - v0;
# m4x = 1642 - u0;
# m4y = 204 - v0;

def get_wh_ratio(m1, m2, m3, m4, width, height):
    u0 = width / 2
    v0 = height / 2
    
    m1x = m1[0] - u0;
    m1y = m1[1] - v0;
    m2x = m2[0] - u0;
    m2y = m2[1] - v0;
    m3x = m3[0] - u0;
    m3y = m3[1] - v0;
    m4x = m4[0] - u0;
    m4y = m4[1] - v0;
    
        # temporary variables k2, k3
    k2 = ((m1y - m4y)*m3x - (m1x - m4x)*m3y + m1x*m4y - m1y*m4x) / ((m2y - m4y)*m3x - (m2x - m4x)*m3y + m2x*m4y - m2y*m4x) 

    k3 = ((m1y - m4y)*m2x - (m1x - m4x)*m2y + m1x*m4y - m1y*m4x) / ((m3y - m4y)*m2x - (m3x - m4x)*m2y + m3x*m4y - m3y*m4x)

    # f_squared is the focal length of the camera, squared
    # if k2==1 OR k3==1 then this equation is not solvable
    # if the focal length is known, then this equation is not needed
    # in that case assign f_squared= sqr(focal_length)
    f_squared = -((k3*m3y - m1y)*(k2*m2y - m1y) + (k3*m3x - m1x)*(k2*m2x - m1x)) / ((k3 - 1)*(k2 - 1))

    #The width/height ratio of the original rectangle
    whRatio = sqrt( 
        (sqr(k2 - 1) + sqr(k2*m2y - m1y)/f_squared + sqr(k2*m2x - m1x)/f_squared) /
        (sqr(k3 - 1) + sqr(k3*m3y - m1y)/f_squared + sqr(k3*m3x - m1x)/f_squared) 
    )


    # if k2==1 AND k3==1, then the focal length equation is not solvable 
    # but the focal length is not needed to calculate the ratio.
    # I am still trying to figure out under which circumstances k2 and k3 become 1
    # but it seems to be when the rectangle is not distorted by perspective, 
    # i.e. viewed straight on. Then the equation is obvious:
    if (k2==1 and k3==1):
        whRatio = sqrt( 
        (sqr(m2y-m1y) + sqr(m2x-m1x)) / 
        (sqr(m3y-m1y) + sqr(m3x-m1x)))


    # After testing, I found that the above equations 
    # actually give the height/width ratio of the rectangle, 
    # not the width/height ratio. 
    # If someone can find the error that caused this, 
    # I would be most grateful.
    # until then:
    return 1 / whRatio

h, w, c = image.shape
print(image.shape)
print(get_wh_ratio((pts[0]), pts[1], pts[2], pts[3], w, h))
"""[[[ 987  213]]

 [[ 466  284]]

 [[ 514  610]]

 [[1036  535]]]
 [[ 988  214]]

 [[ 467  279]]

 [[ 513  611]]

 [[1036  536]]]
    """
# print(get_wh_ratio((546, 546), (1151, 387), (514, 147), (1033, 82), w, h))
# print(get_wh_ratio((514, 610), (1036, 535), (466, 284), (988, 213), w, h))
# print(get_wh_ratio((513, 611), (1036, 536), (467, 279), (987, 214), w, h))
"""
[743 542]]

 [[771  34]]

 [[508   0]]

 [[504 535]
"""
# print(get_wh_ratio((504, 535), (743, 542), (508, 0), (771, 34), w, h))
