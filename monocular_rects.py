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
    
frame = cv2.imread('cropp.png')
# frame = cv2.imread('data/camera_roll/image14.jpg')

input_batch = transform(frame).to(device)

with torch.no_grad():
    prediction = midas(input_batch)

    prediction = torch.nn.functional.interpolate(
        prediction.unsqueeze(1),
        size=frame.shape[:2],
        mode="bicubic",
        align_corners=False,
    ).squeeze()
    
output = prediction.cpu().numpy() / 2048
output = np.clip(output, a_min=0, a_max=1)
output = output * 255
output = output.astype(np.uint8)

print(output.max())
print(output.shape)
print(output)

print(type(output))
cv2.imshow("frame", frame)
cv2.waitKey()
cv2.destroyAllWindows()

cv2.imshow("output", output)
cv2.waitKey()
cv2.destroyAllWindows()

def maxl(l): return l.index(max(l))

def find_rect(i_inp, i_bin):
    contours, hierarchy = cv2.findContours(i_bin, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cnt_largest_i = maxl(list(cv2.contourArea(c) for c in contours))
    cnt_largest = contours[cnt_largest_i]
    
    print("contours", cnt_largest)

    cv2.polylines(i_inp, pts=[cnt_largest], isClosed=False, color=(255, 0, 0), thickness=3)

    epsilon = 0.02 * cv2.arcLength(cnt_largest, True)
    approx = cv2.approxPolyDP(cnt_largest, epsilon, True)
    approx = approx[len(approx) - 4:]

    cv2.polylines(i_inp, pts=[approx], isClosed=False, color=(0, 255, 0), thickness=6)

    print(approx)

    cv2.imshow('img', i_inp)
    cv2.waitKey(0)

def threshold(i_inp):
    
    # i_inp = sharpen(1.0, 0, i_inp)
    
    cv2.imshow('img', i_inp)
    cv2.waitKey(0)
    
    global i_bin, i_blur
    
    i_blur = cv2.GaussianBlur(i_inp, (5, 5), 0)
    i_blur = cv2.medianBlur(i_inp, 11)
    
    cv2.imshow('img', i_blur)
    cv2.waitKey(0)
    
    i_bin = cv2.threshold(i_blur, thresh, 255, cv2.THRESH_BINARY)[1]

    cv2.imshow('img', i_bin)
    cv2.waitKey(0)

    i_bin = cv2.threshold(i_blur, thresh, 255, cv2.THRESH_BINARY)[1]
    
    return i_bin

thresh = 0
def changeThreshold(val):
    global thresh
    global i_bin, i_blur
    thresh = val
    i_bin = cv2.threshold(i_blur, val, 255, cv2.THRESH_BINARY)[1]

    cv2.imshow('img', i_bin)

    cv2.imshow('img', i_bin)

cv2.namedWindow("img")
cv2.createTrackbar("threshold", "img" , thresh, 255, changeThreshold)

print(output)

i_bin = output
i_blur = output
bin_1 = threshold(output)
frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
i_bin = frame_gray
i_blur = frame_gray
bin_2 = threshold(frame_gray)

anded = cv2.bitwise_and(bin_1, bin_2)

cv2.imshow("combined", anded)
cv2.waitKey()
cv2.destroyAllWindows()

find_rect(frame, anded)