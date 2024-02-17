import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt 

cap_left = cv.VideoCapture(0)
cap_right = cv.VideoCapture(1)

def undistort(img):
    ret = 2.2063746245104525
    mtx = np.array([
        [1.09530534e+03, 0.00000000e+00, 9.54353075e+02],
        [0.00000000e+00, 1.09011353e+03, 5.41983054e+02],
        [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]
    ])
    dist = np.array([[-0.32290118, 0.09774828, 0.01101426, 0.00701455, -0.01189179]])

    h,  w = img.shape[:2]
    newcameramtx, roi = cv.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))
    
    mapx, mapy = cv.initUndistortRectifyMap(mtx, dist, None, newcameramtx, (w,h), 5)
    dst = cv.remap(img, mapx, mapy, cv.INTER_LINEAR)
    # crop the image
    x, y, w, h = roi
    x = x + 50
    y = y + 50
    w = w - 50
    h = h - 50
    dst = dst[y:y+h, x:x+w]
    
    return dst

while cap_left.isOpened() and cap_right.isOpened():
    ret_left, frame_left = cap_left.read()
    ret_right, frame_right = cap_right.read()
    
    if ret_left and ret_right:
        clean_left = undistort(frame_left)
        clean_right = undistort(frame_right)
        
        clean_left = cv.cvtColor(clean_left, cv.COLOR_BGR2GRAY)
        clean_right = cv.cvtColor(clean_right, cv.COLOR_BGR2GRAY)
        
        blockSize = 16

        stereo = cv.StereoSGBM_create(minDisparity=0,
                                    numDisparities=64,
                                    blockSize=blockSize,
                                    P1=3*8*blockSize**2,
                                    P2=3*32*blockSize**2,
                                    disp12MaxDiff=1,
                                    uniquenessRatio=15,
                                    speckleWindowSize=0,
                                    speckleRange=2,
                                    preFilterCap=63,
                                    mode=cv.STEREO_SGBM_MODE_SGBM_3WAY)
        
        

        # disparity = stereo.compute(clean_left,clean_right).astype(np.float32) / 512.0
        # window_size = 32
        # min_disp = 0
        # p_factor = 1
        # nDispFactor = 8 # adjust this (14 is good)
        # num_disp = 16*nDispFactor-min_disp

        # stereo = cv.StereoSGBM_create(minDisparity=min_disp,
        #                             numDisparities=num_disp,
        #                             blockSize=window_size,
        #                             P1=p_factor*1*window_size**2,
        #                             P2=p_factor*4*window_size**2,
        #                             disp12MaxDiff=1,
        #                             uniquenessRatio=2,
        #                             speckleWindowSize=0,
        #                             speckleRange=3,
        #                             preFilterCap=63,
        #                             mode=cv.STEREO_SGBM_MODE_SGBM)

        # Compute disparity map
        disparity = stereo.compute(clean_left,clean_right).astype(np.float32) / 512.0
        
        combined_clean = np.concatenate((clean_left, clean_right), axis=1)
        combined = np.concatenate((frame_left, frame_right), axis=1)
        
        if cv.waitKey(1) & 0xFF == ord('s'):
            cv.imwrite("left.jpg", clean_left) 
            cv.imwrite("right.jpg", clean_right) 
    
        
        
        # cv.imshow("Stereo View", combined)
        cv.imshow("Left View", frame_left)
        cv.imshow("Right View", frame_right)
        cv.imshow("Undistorted View", combined_clean)
        
        colormap = plt.get_cmap('plasma')
        heatmap = (colormap(disparity) * 2**16).astype(np.uint16)[:,:,:3]
        heatmap = cv.cvtColor(heatmap, cv.COLOR_RGB2BGR)
        
        cv.imshow("disp",disparity)
    
    if cv.waitKey(1) & 0xFF == ord('q'): 
        break
    
cap_left.release()
cap_right.release()

cv.destroyAllWindows()