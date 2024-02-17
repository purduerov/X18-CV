import cv2
import numpy as np

cap = cv2.VideoCapture(0)

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

while cap.isOpened():
    ret, frame = cap.read()
    
    if ret:
        frame = undistort(frame)
        if cv2.waitKey(1) & 0xFF == ord('s'): 
            image = frame
            break
            
        cv2.imshow("Capture", frame)
        
    if cv2.waitKey(1) & 0xFF == ord('q'): 
        break

# Display the image
cap.release()


i_bin = image
i_blur = image



def maxl(l): return l.index(max(l))

def find_rect(i_inp):
    
    # i_inp = sharpen(1.0, 0, i_inp)
    
    cv2.imshow('img', i_inp)
    cv2.waitKey(0)
    
    global i_bin, i_blur
    
    i_gray = cv2.cvtColor(i_inp, cv2.COLOR_BGR2GRAY)
    i_blur = cv2.GaussianBlur(i_gray, (11, 11), 0)
    i_blur = cv2.medianBlur(i_gray, 25)
    

    cv2.imshow('img', i_blur)
    cv2.waitKey(0)
    
    i_bin = cv2.threshold(i_blur, thresh, 255, cv2.THRESH_BINARY)[1]

    cv2.imshow('img', i_bin)
    cv2.waitKey(0)

    i_bin = cv2.threshold(i_blur, thresh, 255, cv2.THRESH_BINARY)[1]
    contours, hierarchy = cv2.findContours(i_bin, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cnt_largest_i = maxl(list(cv2.contourArea(c) for c in contours))
    cnt_largest = contours[cnt_largest_i]

    cv2.polylines(i_inp, pts=[cnt_largest], isClosed=False, color=(255, 0, 0), thickness=3)

    epsilon = 0.02 * cv2.arcLength(cnt_largest, True)
    approx = cv2.approxPolyDP(cnt_largest, epsilon, True)

    cv2.polylines(i_inp, pts=[approx], isClosed=False, color=(0, 255, 0), thickness=6)

    print(approx)

    cv2.imshow('img', i_inp)
    cv2.waitKey(0)

    return approx

thresh = 160
def changeThreshold(val):
    global thresh
    global i_bin, i_blur
    thresh = val
    i_bin = cv2.threshold(i_blur, val, 255, cv2.THRESH_BINARY)[1]

    cv2.imshow('img', i_bin)

cv2.namedWindow("img")
cv2.createTrackbar("threshold", "img" , 0, 255, changeThreshold)


quad = find_rect(image)