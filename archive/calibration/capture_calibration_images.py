import cv2 as cv
import numpy as np

cap = cv.VideoCapture(0)

counter = 0 

while cap.isOpened():
    ret, frame = cap.read()
    
    if ret:
        if cv.waitKey(1) & 0xFF == ord('e'): 
            cv.imwrite("data/calibration/img" + str(counter) + ".jpg", frame)
            
            print("writing")
            
            counter += 1
            
        font = cv.FONT_HERSHEY_SIMPLEX 
  
        cv.putText(frame,  
                    'Images Taken: ' + str(counter),  
                    (50, 50),  
                    font, 1,  
                    (0, 255, 255),  
                    2,  
                    cv.LINE_4) 
    
        
        cv.imshow("camera view", frame)
        
    if cv.waitKey(1) & 0xFF == ord('q'): 
        break
    
cap.release()
cv.destroyAllWindows()