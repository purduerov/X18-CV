import cv2
import torch
from numpy import savetxt
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
        
cv2.namedWindow('output')
def maxl(l):
    if len(l) == 0:
        return -1
    return l.index(max(l))

def monocify(frame):
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
    
    return output