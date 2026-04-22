import cv2
import depthai as dai
import os
import time

# 1. Create directory for the negative samples
output_dir = "negatives"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 2. Setup Pipeline
pipeline = dai.Pipeline()

cam_rgb = pipeline.create(dai.node.ColorCamera)
cam_rgb.setBoardSocket(dai.CameraBoardSocket.RGB)
cam_rgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
cam_rgb.setInterleaved(False)
cam_rgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)

xout_video = pipeline.create(dai.node.XLinkOut)
xout_video.setStreamName("video")
cam_rgb.video.link(xout_video.input)

# 3. Collection Loop
with dai.Device(pipeline) as device:
    q_video = device.getOutputQueue(name="video", maxSize=4, blocking=False)
    
    print("--- NEGATIVE DATA COLLECTOR ---")
    print("Press 's' to save a negative sample (Image + Empty Label)")
    print("Press 'q' to quit")

    counter = 0
    while True:
        in_video = q_video.get()
        frame = in_video.getCvFrame()

        # Display the feed
        display_frame = frame.copy()
        cv2.putText(display_frame, "READY TO COLLECT", (20, 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow("Negative Collector", display_frame)

        key = cv2.waitKey(1) & 0xFF
        
        # Save logic
        if key == ord('s'):
            timestamp = int(time.time())
            img_filename = f"neg_{timestamp}_{counter}.jpg"
            lbl_filename = f"neg_{timestamp}_{counter}.txt"
            
            # Save the image
            cv2.imwrite(os.path.join(output_dir, img_filename), frame)
            
            # Create the EMPTY label file (This is the crucial part for YOLO)
            with open(os.path.join(output_dir, lbl_filename), "w") as f:
                pass # Writing nothing creates an empty file
            
            print(f"Saved: {img_filename}")
            counter += 1

        elif key == ord('q'):
            break

cv2.destroyAllWindows()