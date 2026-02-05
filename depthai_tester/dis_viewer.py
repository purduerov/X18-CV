import cv2
import depthai as dai
import numpy as np

pipeline = dai.Pipeline()

# Nodes
cam_rgb = pipeline.create(dai.node.ColorCamera)
monoLeft = pipeline.create(dai.node.MonoCamera)
monoRight = pipeline.create(dai.node.MonoCamera)
stereo = pipeline.create(dai.node.StereoDepth)

xout_rgb = pipeline.create(dai.node.XLinkOut)
xout_depth = pipeline.create(dai.node.XLinkOut)

xout_rgb.setStreamName("rgb")
xout_depth.setStreamName("depth")

# Properties
cam_rgb.setPreviewSize(640, 400)
cam_rgb.setInterleaved(False)
cam_rgb.setBoardSocket(dai.CameraBoardSocket.CAM_A)

monoLeft.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
monoRight.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)

# Alignment is key
stereo.setLeftRightCheck(True)
stereo.setDepthAlign(dai.CameraBoardSocket.CAM_A)
# Add this to your StereoDepth config
stereo.setRectifyEdgeFillColor(0) # Black pixels for out-of-view
# For Wide models, use a '1' or '0' alpha to manage the crop
stereo.setAlphaScaling(1)
# Linking
monoLeft.out.link(stereo.left)
monoRight.out.link(stereo.right)
cam_rgb.preview.link(xout_rgb.input)
stereo.depth.link(xout_depth.input)

# Globals for mouse
mouse_x, mouse_y = 320, 200 # Default to center

def mouse_callback(event, x, y, flags, param):
    global mouse_x, mouse_y
    if event == cv2.EVENT_MOUSEMOVE:
        mouse_x, mouse_y = x, y

with dai.Device(pipeline) as device:
    q_depth = device.getOutputQueue(name="depth", maxSize=4, blocking=False)
    q_rgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)

    intrinsics = device.readCalibration().getCameraIntrinsics(dai.CameraBoardSocket.CAM_A, 640, 400)
    fx, fy, cx, cy = intrinsics[0][0], intrinsics[1][1], intrinsics[0][2], intrinsics[1][2]

    # cv2.namedWindow("RGB")
    # cv2.setMouseCallback("RGB", mouse_callback)
    # cv2.namedWindow("disp", cv2.WINDOW_NORMAL)
    # cv2.resizeWindow('disp', 640, 400)
    # cv2.setMouseCallback("disp", mouse_callback)
    # Use WINDOW_NORMAL to enable resizing and moving
    cv2.namedWindow("RGB", cv2.WINDOW_NORMAL)
    cv2.namedWindow("disp", cv2.WINDOW_NORMAL)

    # Set identical sizes
    cv2.resizeWindow("RGB", 1280, 800)
    cv2.resizeWindow("disp", 1280, 800)

    # Move both to the EXACT same screen coordinates (X, Y)
    # This stacks "RGB" directly on top of "disp"
    cv2.moveWindow("disp", 100, 100)
    cv2.moveWindow("RGB", 100, 100)

    cv2.setMouseCallback("RGB", mouse_callback)
    cv2.setMouseCallback("disp", mouse_callback)
    while True:
        frame_depth = q_depth.get().getFrame()
        frame_rgb = q_rgb.get().getCvFrame()

        # Boundary check to prevent crashing if mouse is at the very edge
        # m_y = max(1, min(mouse_y, 398))
        # m_x = max(1, min(mouse_x, 638))

        # Get depth (averaging a small 3x3 area for stability)
        # roi = frame_depth[m_y-1:m_y+2, m_x-1:m_x+2]
        z = frame_depth[mouse_y, mouse_x]

        if z > 0:
            x_mm = (mouse_x - cx) * z / fx
            y_mm = (mouse_y - cy) * z / fy
            label = f"X: {int(x_mm/10)} Y: {int(y_mm/10)} Z: {int(z/10)} in cm"
        else:
            label = "Z: Invalid (Too close or low texture)"
            color = (0, 0, 255) # Red for invalid

        # UI Overlay
        disp_frame = cv2.normalize(frame_depth, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
        disp_frame = cv2.applyColorMap(disp_frame, cv2.COLORMAP_JET)
        cv2.putText(disp_frame, label, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.circle(disp_frame, (mouse_x, mouse_y), 5, (255, 255, 255), -1)
        cv2.putText(frame_rgb, label, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.circle(frame_rgb, (mouse_x, mouse_y), 5, (255, 255, 255), -1)

        cv2.imshow("RGB", frame_rgb)
        cv2.imshow("disp", disp_frame)
        if cv2.waitKey(1) == ord('q'):
            break