import cv2
import depthai as dai
import numpy as np

pipeline = dai.Pipeline()

# Nodes
cam_rgb = pipeline.create(dai.node.ColorCamera)
monoLeft = pipeline.create(dai.node.MonoCamera)
monoRight = pipeline.create(dai.node.MonoCamera)
stereo = pipeline.create(dai.node.StereoDepth)

# Create a PostProcessing object to modify

# # Now enable the filters on that object
# stereo.initialConfig.PostProcessing().spatialFilter.enable = True
# stereo.initialConfig.PostProcessing().spatialFilter.holeFillingRadius = 5
# stereo.initialConfig.PostProcessing().spatialFilter.numIterations = 1
# stereo.initialConfig.PostProcessing().temporalFilter.enable = True
# stereo.initialConfig.PostProcessing().temporalFilter.persistencyMode = dai.RawStereoDepthConfig.PostProcessing.TemporalFilter.PersistencyMode.VALID_2_IN_LAST_4


# # Set other parameters directly on config
# stereo.initialConfig.setConfidenceThreshold(230)
# stereo.initialConfig.setMedianFilter(dai.MedianFilter.KERNEL_7x7)
stereo.setSubpixel(True)
stereo.setExtendedDisparity(True)

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
    z_ref = frame_depth[center_y, center_x]
    z_temp = z_ref
    top = center_y
    y_top = 0
    while(top > 1):
        z_i = frame_depth[top, center_x]
        if z_i == 0:
            top -= 1
            continue
        if abs(np.int32(z_i) - np.int32(z_temp)) > 100:
            y_top = top + 1
            break 
        z_temp = z_i
        top -= 1
    bottom = center_y
    y_bottom = 0
    while (bottom < center_y * 2):
        z_i = frame_depth[bottom, center_x]
        if z_i == 0: 
            bottom += 1
            continue
        if abs(np.int32(z_i) - np.int32(z_temp)) > 100:
            y_bottom = bottom - 1
            break 
        z_temp = z_i
        bottom += 1
    z_top = frame_depth[y_top, center_x]
    z_bottom = frame_depth[y_bottom, center_x]

    z_ref = frame_depth[center_y, center_x]
    z_t = z_top if z_top > 0 else z_ref
    z_b = z_bottom if z_bottom > 0 else z_ref
    bottom = get_cm(y_bottom, cy, fy, z_b)
    top = get_cm(y_top, cy, fy, z_t)
    length = abs(bottom - top) / 10
    return y_top, y_bottom

top = -1
bottom = -1

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
            x_mm = get_cm(mouse_x, cx, fx, z)
            y_mm = get_cm(mouse_y, cy, fy, z)
            if x_mm != (mouse_x - cx) * z / fx or y_mm != (mouse_y - cy) * z / fy:
                print('FAAAAH')
                exit(0)
            label = f"X: {int(x_mm/10)} Y: {int(y_mm/10)} Z: {int(z/10)} in cm"
        else:
            label = "Z: Invalid (Too close or low texture)"
            color = (0, 0, 255) # Red for invalid
        label += f" Length is {length:.2f}"
        # UI Overlay
        disp_frame = cv2.normalize(frame_depth, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
        disp_frame = cv2.applyColorMap(disp_frame, cv2.COLORMAP_JET)
        cv2.putText(disp_frame, label, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        # cv2.circle(disp_frame, (mouse_x, mouse_y), 5, (255, 255, 255), -1)
        cv2.putText(frame_rgb, label, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        # cv2.circle(frame_rgb, (mouse_x, mouse_y), 5, (255, 255, 255), -1)

        center_y, center_x = frame_rgb.shape[:2]
        cv2.drawMarker(frame_rgb, (center_x  // 2, center_y // 2), (0, 0, 255), 
               markerType=cv2.MARKER_CROSS, 
               markerSize=30, 
               thickness=2)
        center_y, center_x = disp_frame.shape[:2]
        cv2.drawMarker(disp_frame, (center_x // 2, center_y // 2), (0, 0, 255), 
               markerType=cv2.MARKER_CROSS, 
               markerSize=30, 
               thickness=2)
        if bottom != -1 and top != -1:
            bottom_coord = (center_x // 2, bottom)
            top_coord = (center_x // 2, top) 
            # cv2.line(disp_frame, bottom_coord, top_coord, (255, 0, 0), 5)
            cv2.line(disp_frame, bottom_coord, top_coord, (255, 255, 255), 2)
            # cv2.circle(disp_frame, center=bottom_coord, radius = 1, color = (255, 255, 255), thickness = 2)
            # cv2.circle(disp_frame, center=top_coord, radius = 1, color = (255, 255, 255), thickness = 2)
        key = cv2.waitKey(1)
        if key == ord('q'):
            break
        if key == ord('e'):
            top, bottom = find_length(frame_depth, center_x // 2, center_y // 2, fy, cy)
        cv2.imshow("RGB", frame_rgb)
        cv2.imshow("disp", disp_frame)