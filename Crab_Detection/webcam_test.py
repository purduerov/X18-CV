import cv2
import depthai as dai
from ultralytics import YOLO

# 1. Load your YOLO model
model = YOLO(r'C:\Users\User\ROV\X18-CV\Crab_Detection\best.pt')

# Create the pipeline
pipeline = dai.Pipeline()

# 2. Explicitly create the ColorCamera node
cam_rgb = pipeline.create(dai.node.ColorCamera)
cam_rgb.setBoardSocket(dai.CameraBoardSocket.CAM_A) # Standard for OAK-D center camera
cam_rgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
cam_rgb.setInterleaved(False)
cam_rgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)
cam_rgb.setFps(30)

# 3. Explicitly create the XLinkOut node
xout_video = pipeline.create(dai.node.XLinkOut)
xout_video.setStreamName("video")

# 4. Link the camera output to the XLink input
cam_rgb.video.link(xout_video.input)

# Connect to the OAK-D device and start the pipeline
with dai.Device(pipeline) as device:
    # Get the output queue for the "video" stream defined above
    q_video = device.getOutputQueue(name="video", maxSize=4, blocking=False)

    print("MATE ROV: OAK-D Online. Press 'q' to quit.")

    while True:
        # 5. Retrieve the frame from the OAK-D hardware
        in_video = q_video.get() 
        frame = in_video.getCvFrame()

        # 6. Run YOLOv8 inference on the frame
        # verbose=False keeps your terminal clean from prediction logs
        results = model(frame, conf=0.5, verbose=False)
        r = results[0]

        # 7. Count specifically the Invasive Green Crab (Class 0)
        count_green = 0
        if len(r.boxes) > 0:
            # We filter for class 0 and sum up the occurrences
            count_green = (r.boxes.cls == 0).sum().item()

        # 8. Visualize detections and overlay the count
        annotated_frame = r.plot()
        
        cv2.putText(
            annotated_frame,
            f"European Green Crabs: {int(count_green)}",
            (40, 70), # Positioning the text
            cv2.FONT_HERSHEY_SIMPLEX,
            1.5,
            (0, 255, 0), # Green color in BGR
            3
        )

        # 9. Display the video feed
        cv2.imshow("ROV Underwater Vision", annotated_frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cv2.destroyAllWindows()