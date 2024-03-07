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


# for i  in range(1, 10):
if True:
    ret = True
    # frame = cv2.imread('data/camera_roll/image4.jpg')
    frame = cv2.imread('data/camera_roll/image14.jpg')
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
            
        output = prediction.cpu().numpy()
        cv2.imshow("frame", frame)    
        cv2.imshow("output", output/2048)
        
        savetxt('data.csv', output, delimiter=',')
        
        
        cv2.waitKey()
    
# cap.release()
# out.release()
  
# De-allocate any associated memory usage  
cv2.destroyAllWindows() 
