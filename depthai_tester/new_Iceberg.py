import cv2
import depthai as dai
import numpy as np

pipeline = dai.Pipeline()

# Nodes
monoLeft = pipeline.create(dai.node.MonoCamera)
monoRight = pipeline.create(dai.node.MonoCamera)
stereo = pipeline.create(dai.node.StereoDepth)

xout_depth = pipeline.create(dai.node.XLinkOut)

xout_depth.setStreamName("depth")

monoLeft.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
monoRight.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)

# Shadow & Noise Mitigation (DepthAI 2.31.1 Syntax)
stereo.initialConfig.PostProcessing().spatialFilter.enable = True
stereo.initialConfig.PostProcessing().spatialFilter.holeFillingRadius = 5
stereo.initialConfig.PostProcessing().spatialFilter.numIterations = 1

stereo.initialConfig.PostProcessing().temporalFilter.enable = True
stereo.initialConfig.PostProcessing().temporalFilter.persistencyMode = dai.RawStereoDepthConfig.PostProcessing.TemporalFilter.PersistencyMode.VALID_2_IN_LAST_4

# 2. These methods usually work fine as direct setters on the config object
stereo.initialConfig.setConfidenceThreshold(235)
stereo.initialConfig.setMedianFilter(dai.MedianFilter.KERNEL_7x7)
# Stereo Settings
stereo.setLeftRightCheck(True)
stereo.setSubpixel(True) # Crucial for accuracy on large objects
stereo.setExtendedDisparity(True)
# Linking
monoLeft.out.link(stereo.left)
monoRight.out.link(stereo.right)
stereo.depth.link(xout_depth.input)

# Globals for mouse
mouse_x, mouse_y = 320, 200 # Default to center

length = -1

def get_cm(y_pos, cy, fy, z):
    return (y_pos - cy) * z / fy

def find_length(frame_depth, center_x, center_y, fy, cy):
    global length
    z_ref = frame_depth[center_y, center_x]
    if z_ref == 0: return 0, 0 # Can't measure if center is invalid
    
    z_temp = z_ref
    
    # --- UPWARD SEARCH ---
    y_top = 1 # Default to top of screen
    for top in range(center_y, 1, -1):
        z_i = frame_depth[top, center_x]
        if z_i == 0: continue 
        if abs(np.int32(z_i) - np.int32(z_temp)) > 100:
            y_top = top + 1
            break
        z_temp = z_i
        y_top = top

    # --- DOWNWARD SEARCH ---
    h = frame_depth.shape[0]
    y_bottom = h - 1 # Default to bottom of screen
    z_temp = z_ref # Reset temp to center for the second half
    for bottom in range(center_y, h - 1):
        z_i = frame_depth[bottom, center_x]
        if z_i == 0: continue
        if abs(np.int32(z_i) - np.int32(z_temp)) > 100:
            y_bottom = bottom - 1
            break
        z_temp = z_i
        y_bottom = bottom

    # --- COORDINATE CALCULATION ---
    z_t = frame_depth[y_top, center_x]
    z_b = frame_depth[y_bottom, center_x]
    
    # Fallback to z_ref if the edges are in shadow/holes
    final_zt = z_t if z_t > 0 else z_ref
    final_zb = z_b if z_b > 0 else z_ref

    # Back-project to physical Y coordinates
    phys_top = (y_top - cy) * final_zt / fy
    phys_bottom = (y_bottom - cy) * final_zb / fy

    length = abs(phys_bottom - phys_top) / 10.0 # cm
    return y_top, y_bottom
 
def mouse_callback(event, x, y, flags, param):
    global mouse_x, mouse_y
    if event == cv2.EVENT_MOUSEMOVE:
        mouse_x, mouse_y = x, y

bottom = -1
top = -1

with dai.Device(pipeline) as device:
    q_depth = device.getOutputQueue(name="depth", maxSize=4, blocking=False)

    intrinsics = device.readCalibration().getCameraIntrinsics(dai.CameraBoardSocket.CAM_A, 640, 400)
    fx, fy, cx, cy = intrinsics[0][0], intrinsics[1][1], intrinsics[0][2], intrinsics[1][2]
    # print(fx, fy, cx, cy)

    # cv2.namedWindow("RGB")
    # cv2.setMouseCallback("RGB", mouse_callback)
    # cv2.namedWindow("disp", cv2.WINDOW_NORMAL)
    # cv2.resizeWindow('disp', 640, 400)
    # cv2.setMouseCallback("disp", mouse_callback)
    # Use WINDOW_NORMAL to enable resizing and moving
    cv2.namedWindow("disp", cv2.WINDOW_NORMAL)

    # Set identical sizes
    cv2.resizeWindow("disp", 1280, 800)

    # Move both to the EXACT same screen coordinates (X, Y)
    # This stacks "RGB" directly on top of "disp"
    cv2.moveWindow("disp", 100, 100)

    # cv2.setMouseCallback("disp", mouse_callback)
    while True:
        frame_depth = q_depth.get().getFrame()

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
        label += f' Length is {length:.2f}'
        # UI Overlay
        disp_frame = cv2.normalize(frame_depth, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
        disp_frame = cv2.applyColorMap(disp_frame, cv2.COLORMAP_JET)
        center_y, center_x = disp_frame.shape[:2]
        cv2.drawMarker(disp_frame, (center_x // 2, center_y // 2), (0, 0, 255), 
               markerType=cv2.MARKER_CROSS, 
               markerSize=30, 
               thickness=2)
        cv2.putText(disp_frame, label, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        # cv2.circle(disp_frame, (mouse_x, mouse_y), 5, (255, 255, 255), -1)

        if bottom != -1 and top != -1:
          bottom_coord = (center_x // 2, bottom)
          top_coord =  (center_x // 2, top)

          cv2.circle(disp_frame, center=bottom_coord, radius = 1, color = (255, 255, 255), thickness = 2)
          cv2.circle(disp_frame, center=top_coord, radius = 1, color = (255, 255, 255), thickness = 2)
        key = cv2.waitKey(1)
        if key == ord('q'):
            break
        elif key == ord('e'):
          top, bottom = find_length(frame_depth, center_x // 2, center_y // 2, fy, cy)
        cv2.imshow("disp", disp_frame)
