from transformers import pipeline
from PIL import Image
import cv2 
import numpy as np

checkpoint = "vinvino02/glpn-nyu"
depth_estimator = pipeline("depth-estimation", model=checkpoint)

cap = cv2.VideoCapture(0)

def mouseValue(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDOWN: #checks mouse left button down condition
        value = depth[y,x]
        print(value)
        # print("inches: ", 136 * math.exp(-1.35E-03 * value))
        # y = -0.0107*x + 30.2
        # 136 e^-1.35E-03x
        
cv2.namedWindow('output')
cv2.setMouseCallback('output',mouseValue)


for i  in range(1, 10):
    ret = True
    frame = cv2.imread('data/validation/val' + str(i) + '.jpg')

while(True): 
    ret, frame = cap.read()  
    
    if ret:
        color_coverted = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) 
        pil_image = Image.fromarray(color_coverted)
        pil_image.thumbnail((1000, 1000))
        
        predictions = depth_estimator(pil_image)
        depth = np.array(predictions["depth"])
        
        cv2.imshow('output', depth)  
        cv2.imshow('frame', frame)  
        
    if cv2.waitKey(1) & 0xFF == ord('q'): 
        break
    # cv2.waitKey()
    
cap.release()
  
# De-allocate any associated memory usage  
cv2.destroyAllWindows() 
