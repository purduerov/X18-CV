import cv2
import torch
import urllib.request
from numpy import savetxt

import matplotlib.pyplot as plt
import numpy as np
import math

# model_type = "MiDaS_small"
model_type = "DPT_Hybrid"

midas = torch.hub.load("intel-isl/MiDaS", model_type)

# # if not torch.backends.mps.is_available():
# #     if not torch.backends.mps.is_built():
# #         print("MPS not available because the current PyTorch install was not "
# #               "built with MPS enabled.")
# #     else:
# #         print("MPS not available because the current MacOS version is not 12.3+ "
# #               "and/or you do not have an MPS-enabled device on this machine.")
# #     device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
# # else:
# #     device = torch.device("mps")
device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")

# print(device)
# midas.to(device)
# midas.eval()

midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms")

if model_type == "DPT_Large" or model_type == "DPT_Hybrid":
    transform = midas_transforms.dpt_transform
else:
    transform = midas_transforms.small_transform
    
def maxl(l):
    if len(l) == 0:
        return -1
    return l.index(max(l))

cap = cv2.VideoCapture('data/camera_roll/video1.avi')

def depth(frame):
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
    
    return output

count = 0

while cap.isOpened():
    ret, frame = cap.read()
    
    if not ret:
        break;
    
    cap.set(cv2.CAP_PROP_POS_FRAMES, count)
    count += 15

    
    print(frame.shape)
    
    # frame = frame[100:500, 200:1200]
    
    output = depth(frame)
    
    avg = np.mean(output) * 0.65
    
    i_bin2 = cv2.threshold(output, avg, 255, cv2.THRESH_BINARY)[1]
    print(avg)
    
    i_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    i_blur = cv2.GaussianBlur(i_gray, (5, 5), 0)
    i_blur = cv2.medianBlur(i_blur, 11)
    
    i_bin = cv2.threshold(i_blur, 145, 255, cv2.THRESH_BINARY)[1]
    
    final = cv2.bitwise_and(i_bin, i_bin2)
    
    morph_size = 4
    
    element = cv2.getStructuringElement(2, (2*morph_size + 1, 2*morph_size+1), (morph_size, morph_size))
    final = cv2.morphologyEx(final, cv2.MORPH_OPEN, element)
    # cv.imshow(title_window, dst)
    
    # print(i_bin.sum())
    
    contours, hierarchy = cv2.findContours(final, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cnt_largest_i = maxl(list(cv2.contourArea(c) for c in contours))
    
    if cnt_largest_i == -1:
        continue;
    
    cnt_largest = contours[cnt_largest_i]

    cv2.polylines(frame, pts=[cnt_largest], isClosed=False, color=(255, 0, 0), thickness=3)

    epsilon = 0.02 * cv2.arcLength(cnt_largest, True)
    approx = cv2.approxPolyDP(cnt_largest, epsilon, True)
    approx = approx[len(approx) - 4:]

    cv2.polylines(frame, pts=[approx], isClosed=False, color=(0, 255, 0), thickness=6)
    
    cv2.imshow("output", i_bin)
    cv2.imshow("bin_depth", i_bin2)
    cv2.imshow("output_depth", output)
    cv2.imshow("output_final", final)
    cv2.imshow("frame", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'): 
        break

cap.release()
cv2.destroyAllWindows()
