import cv2
import torch
import urllib.request
from numpy import savetxt

import matplotlib.pyplot as plt
import numpy as np
import math

model_type = "DPT_Hybrid"

midas = torch.hub.load("intel-isl/MiDaS", model_type)

device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
midas.to(device)
midas.eval()

midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms")

if model_type == "DPT_Large" or model_type == "DPT_Hybrid":
    transform = midas_transforms.dpt_transform
else:
    transform = midas_transforms.small_transform

# cap = cv2.VideoCapture(0)
# cap = cv2.VideoCapture('monocular_depth/driving test 11_11.mov')
# fourcc = cv2.VideoWriter_fourcc(*'XVID')
# out = cv2.VideoWriter('output.avi', fourcc, 20.0, (1920,  1080))

def mouseValue(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDOWN: #checks mouse left button down condition
        value = output[y,x]
        print("value: ", value)
        print("inches: ", 136 * math.exp(-1.35E-03 * value))
        # y = -0.0107*x + 30.2
        # 136 e^-1.35E-03x
        
cv2.namedWindow('output')
cv2.setMouseCallback('output',mouseValue)

def maxl(l):
    if len(l) == 0:
        return -1
    return l.index(max(l))


# for i  in range(1, 10):
if True:
    ret = True
    # frame = cv2.imread('data/camera_roll/image4.jpg')
    # frame = cv2.imread('data/camera_roll/image10.jpg')
    # frame = cv2.imread('cropp.png')
    frame = cv2.imread('crop2.png')
# while cap.isOpened():
#     ret, frame = cap.read()
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        input_batch = transform(frame).to(device)
        
        with torch.no_grad():
            prediction = midas(input_batch)

            prediction = torch.nn.functional.interpolate(
                prediction.unsqueeze(1),
                size=frame.shape[:2],
                mode="bicubic",
                align_corners=False,
            ).squeeze()
            
        output = prediction.cpu().numpy() / 3072
        output = np.clip(output, a_min=0, a_max=1)
        output = output * 255
        output = output.astype(np.uint8)
    
        avg = np.mean(output) * 1
        
        i_bin2 = cv2.threshold(output, avg, 255, cv2.THRESH_BINARY)[1]
        
        i_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
        i_blur = cv2.GaussianBlur(i_gray, (5, 5), 0)
        i_blur = cv2.medianBlur(i_blur, 11)
        
        i_bin = cv2.threshold(i_blur, 130, 255, cv2.THRESH_BINARY)[1]
        
        morph_size = 4
    
        element = cv2.getStructuringElement(2, (2*morph_size + 1, 2*morph_size+1), (morph_size, morph_size))
        
        final = cv2.bitwise_and(i_bin, i_bin2)
        final = cv2.morphologyEx(final, cv2.MORPH_OPEN, element)
        # cv.imshow(title_window, dst)
        
        # print(i_bin.sum())
        
        contours, hierarchy = cv2.findContours(final, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cnt_largest_i = maxl(list(cv2.contourArea(c) for c in contours))
        
        cnt_largest = contours[cnt_largest_i]

        cv2.polylines(frame, pts=[cnt_largest], isClosed=False, color=(255, 0, 0), thickness=3)

        epsilon = 0.02 * cv2.arcLength(cnt_largest, True)
        approx = cv2.approxPolyDP(cnt_largest, epsilon, True)
        approx = approx[len(approx) - 4:]

        cv2.polylines(frame, pts=[approx], isClosed=False, color=(0, 255, 0), thickness=6)
        
        cv2.imshow("frame", frame)    
        cv2.imshow("output", output/2048)
        cv2.imshow("bin2", i_bin2)
        cv2.imshow("bin", i_bin)
        cv2.imshow("and", final)
        
        savetxt('data.csv', output, delimiter=',')
        
        
        cv2.waitKey()
    
# cap.release()
# out.release()
  
# De-allocate any associated memory usage  
cv2.destroyAllWindows() 
