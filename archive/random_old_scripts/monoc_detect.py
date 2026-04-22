import cv2
from monocular_depth import monocular2
import numpy as np

if True:
    ret = True
    # frame = cv2.imread('data/camera_roll/image4.jpg')
    frame = cv2.imread('data/camera_roll/image10.jpg')
    # frame = cv2.imread('cropp.png')
    # frame = cv2.imread('crop2.png')
# while cap.isOpened():
#     ret, frame = cap.read()
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        output = monocular2.monocify(frame)
    
        thresh1, i_bin2 = cv2.threshold(output, 200, 255, cv2.THRESH_BINARY) #+ cv2.THRESH_OTSU)
        
        # i_bin2 = cv2.threshold(output, avg, 255, cv2.THRESH_BINARY)[1]
        
        i_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
        i_blur = cv2.GaussianBlur(i_gray, (3, 3), 0)
        
        thresh2, i_bin = cv2.threshold(i_blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        # i_bin = cv2.threshold(i_blur, 130, 255, cv2.THRESH_BINARY)[1]
        
        # morph_size = 4
        print(thresh2)
        edge = cv2.Canny(i_blur, 0, thresh2)
        
        height, width, _ = frame.shape
        raw_contours = np.zeros((height, width)).astype(np.uint8)
        
        contours, _ = cv2.findContours(edge, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(raw_contours, contours, -1, (255, 255, 255), 3)
        
        # element = cv2.getStructuringElement(2, (2*morph_size + 1, 2*morph_size+1), (morph_size, morph_size))
        
        final = cv2.bitwise_not(cv2.bitwise_and(i_bin, i_bin2))
        # final = cv2.morphologyEx(final, cv2.MORPH_OPEN, element)
        # cv.imshow(title_window, dst)
        
        # print(i_bin.sum())
        
        contours, hierarchy = cv2.findContours(final, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cnt_largest_i = monocular2.maxl(list(cv2.contourArea(c) for c in contours))
        
        cnt_largest = contours[cnt_largest_i]

        cv2.polylines(frame, pts=[cnt_largest], isClosed=False, color=(255, 0, 0), thickness=3)

        epsilon = 0.02 * cv2.arcLength(cnt_largest, True)
        approx = cv2.approxPolyDP(cnt_largest, epsilon, True)
        approx = approx[len(approx) - 4:]

        cv2.polylines(frame, pts=[approx], isClosed=False, color=(0, 255, 0), thickness=6)
        
        cv2.imshow("output", output/2048)
        cv2.imshow("bin2", i_bin2)
        cv2.imshow("bin", i_bin)
        cv2.imshow("and", final)
        cv2.imshow("edge", raw_contours)
        
        cv2.imshow("frame", frame)    
        
        cv2.waitKey()
cv2.destroyAllWindows() 
