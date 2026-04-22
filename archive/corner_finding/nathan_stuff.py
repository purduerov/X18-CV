import cv2
import numpy as np

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
# cap.release()

image = cv2.imread('image2.jpeg')
cv2.imshow("Capture", image)
key = cv2.waitKey(0)
undistored_img = undistort(image)
cv2.imshow("Capture", undistored_img)
key = cv2.waitKey(0)