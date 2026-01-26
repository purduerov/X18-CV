import cv2
import depthai as dai
import numpy as np

# 1. Pipeline Setup
pipeline = dai.Pipeline()

# Define sources and outputs
cam_rgb = pipeline.create(dai.node.ColorCamera)
nn = pipeline.create(dai.node.MobileNetDetectionNetwork)
xout_rgb = pipeline.create(dai.node.XLinkOut)
xout_nn = pipeline.create(dai.node.XLinkOut)

xout_rgb.setStreamName("rgb")
xout_nn.setStreamName("nn")

# 2. Properties
cam_rgb.setPreviewSize(300, 300) # Input size for MobileNet
cam_rgb.setInterleaved(False)
cam_rgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)

# Download and set the model blob (MobileNet-SSD)
import blobconverter
nn.setBlobPath(blobconverter.from_zoo(name="mobilenet-ssd", shaves=5))
nn.setConfidenceThreshold(0.5)

# 3. Linking
cam_rgb.preview.link(nn.input)
cam_rgb.preview.link(xout_rgb.input)
nn.out.link(xout_nn.input)

# 4. Main Loop
with dai.Device(pipeline) as device:
    q_rgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
    q_nn = device.getOutputQueue(name="nn", maxSize=4, blocking=False)

    while True:
        in_rgb = q_rgb.get()
        in_nn = q_nn.get()

        if in_rgb is not None:
            frame = in_rgb.getCvFrame()
            detections = in_nn.detections

            for detection in detections:
                # Convert normalized coordinates (0-1) to pixel coordinates
                h, w = frame.shape[:2]
                x1 = int(detection.xmin * w)
                y1 = int(detection.ymin * h)
                x2 = int(detection.xmax * w)
                y2 = int(detection.ymax * h)

                # Draw the bounding box
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"ID: {detection.label}", (x1 + 10, y1 + 20), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0))

            cv2.imshow("Object Detection", frame)

        if cv2.waitKey(1) == ord('q'):
            break