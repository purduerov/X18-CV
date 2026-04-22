import cv2
import depthai as dai
from ultralytics import YOLO

# 1. Load model
model = YOLO(r'best_v2.pt')

# 2. Setup v2 Pipeline
pipeline = dai.Pipeline()

# Create Color Camera
cam_rgb = pipeline.create(dai.node.ColorCamera)
cam_rgb.setBoardSocket(dai.CameraBoardSocket.RGB) # OAK-D Pro W center camera
cam_rgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
cam_rgb.setInterleaved(False)
cam_rgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)
cam_rgb.setFps(30)

# Create XLinkOut
xout_video = pipeline.create(dai.node.XLinkOut)
xout_video.setStreamName("video")

# Link Camera -> XLink
cam_rgb.video.link(xout_video.input)

# 3. Execution Loop
with dai.Device(pipeline) as device:
    # Get the output queue
    q_video = device.getOutputQueue(name="video", maxSize=4, blocking=False)

    print("MATE ROV: Running on DepthAI v2 Stable. Press 'q' to quit.")

    while True:
        # Get frame from OAK-D
        in_video = q_video.get() 
        frame = in_video.getCvFrame()

        # Run YOLO inference
        # Change 0.5 to 0.7 or 0.8 to be more "strict"
        results = model(frame, conf=0.65, verbose=False)
        r = results[0]

        # Count Green Crabs (Class 0)
        count_green = 0
        if len(r.boxes) > 0:
            count_green = (r.boxes.cls == 0).sum().item()

        # Generate annotated image
        annotated = r.plot()
        
        # Display Count Overlay
        cv2.putText(
            annotated,
            f"Green Crabs: {int(count_green)}",
            (40, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.5,
            (0, 255, 0),
            2
        )

        cv2.imshow("ROV Crab Detection (v2)", annotated)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cv2.destroyAllWindows()