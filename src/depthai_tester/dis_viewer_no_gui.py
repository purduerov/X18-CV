import cv2
import depthai as dai
import numpy as np

# Create pipeline
pipeline = dai.Pipeline()

# Define sources and outputs
monoLeft = pipeline.create(dai.node.MonoCamera)
monoRight = pipeline.create(dai.node.MonoCamera)
stereo = pipeline.create(dai.node.StereoDepth)
xout_depth = pipeline.create(dai.node.XLinkOut)

xout_depth.setStreamName("depth")

# Properties
monoLeft.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
monoLeft.setBoardSocket(dai.CameraBoardSocket.LEFT)
monoRight.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
monoRight.setBoardSocket(dai.CameraBoardSocket.RIGHT)

# Outputting spatial data requires alignment
stereo.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.HIGH_DENSITY)
stereo.setLeftRightCheck(True)
stereo.setSubpixel(True)

# Linking
monoLeft.out.link(stereo.left)
monoRight.out.link(stereo.right)
stereo.depth.link(xout_depth.input)

# Variables for the mouse callback
mouse_x, mouse_y = 0, 0

def mouse_callback(event, x, y, flags, param):
    global mouse_x, mouse_y
    if event == cv2.EVENT_MOUSEMOVE:
        mouse_x, mouse_y = x, y

with dai.Device(pipeline) as device:
    depth_queue = device.getOutputQueue(name="depth", maxSize=4, blocking=False)
    
    cv2.namedWindow("Depth")
    cv2.setMouseCallback("Depth", mouse_callback)

    # Get intrinsic parameters for coordinate calculation
    calibData = device.readCalibration()
    # Assuming we are looking at the right mono camera frame
    intrinsics = calibData.getCameraIntrinsics(dai.CameraBoardSocket.RIGHT, 640, 400)
    fx, fy, cx, cy = intrinsics[0][0], intrinsics[1][1], intrinsics[0][2], intrinsics[1][2]

    while True:
        in_depth = depth_queue.get()
        depth_frame = in_depth.getFrame() # Depth in millimeters

        # 1. Get Z (Depth)
        # We use a small ROI or a single pixel
        z = depth_frame[mouse_y, mouse_x]

        # 2. Calculate X and Y using the pinhole camera model
        # X = (u - cx) * Z / fx
        # Y = (v - cy) * Z / fy
        if z > 0:
            x_mm = (mouse_x - cx) * z / fx
            y_mm = (mouse_y - cy) * z / fy
            text = f"X: {int(x_mm/10)}mm Y: {int(y_mm/10)}mm Z: {int(z/10)} cm"
        else:
            text = "Out of range"

        # Visualization
        disp_frame = cv2.normalize(depth_frame, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
        disp_frame = cv2.applyColorMap(disp_frame, cv2.COLORMAP_JET)
        cv2.putText(disp_frame, text, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.circle(disp_frame, (mouse_x, mouse_y), 5, (255, 255, 255), -1)
        
        cv2.imshow("Depth", disp_frame)
        if cv2.waitKey(1) == ord('q'):
            break