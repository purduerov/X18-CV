import cv2
import numpy as np
import os

# Import the image
cap = cv2.VideoCapture("/data/camera_roll/video1.avi")

if (cap.isOpened() == False):  
    print("Error reading video file") 
  
# We need to set resolutions. 
# so, convert them from float to integer. 
frame_width = int(cap.get(3)) 
frame_height = int(cap.get(4)) 
   
size = (1484, 585)

vid_count = 0

while os.path.isfile("data/camera_roll/video" + str(vid_count) + ".avi"):
        vid_count += 1

writer = cv2.VideoWriter("data/camera_roll/video" + str(vid_count) + ".avi",  
                         cv2.VideoWriter_fourcc(*'MJPG'), 
                         10, size) 

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
def save_image(image):
    count = 0
    while os.path.isfile("data/camera_roll/image" + str(count) + ".jpg"):
        count += 1

    cv2.imwrite("data/camera_roll/image" + str(count) + ".jpg", image)
    
while cap.isOpened():
    ret, frame = cap.read()
    if ret:
        # frame = undistort(frame)
        cv2.imshow("camera", frame)
        writer.write(frame)
        if cv2.waitKey(1) & 0xFF == ord('s'): 
            save_image(frame)
        
    if cv2.waitKey(1) & 0xFF == ord('q'): 
        break

cap.release()
writer.release()
cv2.destroyAllWindows()
