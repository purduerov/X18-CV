import cv2
import depthai as dai
import numpy as np
from ultralytics import YOLO

# --- NEW: LIGHTING EQUALIZATION FUNCTION ---
def equalize_underwater_lighting(image):
    """ Matches the live feed to the training data preprocessing """
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    # Use the same CLAHE settings used in your training script
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    v = clahe.apply(v)
    return cv2.cvtColor(cv2.merge((h, s, v)), cv2.COLOR_HSV2BGR)

# 1. Load model
model = YOLO(r'C:\Users\User\ROV\X18-CV\Crab_Detection\best3_HSV_1.pt')

# 2. Setup Pipeline (Universal Stable Version)
pipeline = dai.Pipeline()

# Create Color Camera
cam_rgb = pipeline.createColorCamera() # Use the direct creation method
cam_rgb.setBoardSocket(dai.CameraBoardSocket.RGB) # Use RGB for standard OAK-D
cam_rgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
cam_rgb.setInterleaved(False)
cam_rgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)
cam_rgb.setFps(30)

# Create XLinkOut using the direct pipeline method to avoid node attribute errors
xout_video = pipeline.createXLinkOut() 
xout_video.setStreamName("video")

# Link Camera -> XLink
cam_rgb.video.link(xout_video.input)

# 3. Execution Loop
with dai.Device(pipeline) as device:
    q_video = device.getOutputQueue(name="video", maxSize=4, blocking=False)

    print("MATE ROV: Pre-processing enabled. Press 'q' to quit.")

    while True:
        in_video = q_video.get() 
        frame = in_video.getCvFrame()

        # --- CRITICAL STEP: MATCH THE TRAINING DATA ---
        # Equalize the frame BEFORE sending it to the model
        processed_frame = equalize_underwater_lighting(frame)

        # Run YOLO inference on the PROCESSED frame
        results = model(processed_frame, conf=0.8, verbose=False) # Start at 0.5 to test
        r = results[0]

        # Count Crabs (Class 0: Green, 1: Rock, 2: Jonah)
        count_green = (r.boxes.cls == 0).sum().item() if len(r.boxes) > 0 else 0
        count_rock = (r.boxes.cls == 1).sum().item() if len(r.boxes) > 0 else 0

        # Generate annotated image
        annotated = r.plot()
        
        # Display Count Overlay
        cv2.putText(annotated, f"Green: {int(count_green)} | Rock: {int(count_rock)}", 
                    (40, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)

        cv2.imshow("ROV Crab Detection (Processed)", annotated)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cv2.destroyAllWindows()