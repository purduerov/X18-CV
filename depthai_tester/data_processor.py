import cv2
import numpy as np

def get_data(dir):
  frame_depth = np.load(dir + 'frame_depth.npy')
  frame_rgb = np.load(dir + 'frame_rgb.npy')
  intrinsics = np.load(dir + 'intrinsics.npy')
  return frame_depth, frame_rgb, intrinsics

mouse_x, mouse_y = 320, 200 # Default to center

def mouse_callback(event, x, y, flags, param):
      global mouse_x, mouse_y
      if event == cv2.EVENT_MOUSEMOVE:
          mouse_x, mouse_y = x, y

def run_ts(frame_depth, frame_rgb, intrinsics):
  fx, fy, cx, cy = intrinsics[0][0], intrinsics[1][1], intrinsics[0][2], intrinsics[1][2]
  

  cv2.namedWindow("disp", cv2.WINDOW_NORMAL)
  cv2.namedWindow("RGB", cv2.WINDOW_NORMAL)

  # Set identical sizes
  cv2.resizeWindow("disp", 1280, 800)
  cv2.resizeWindow("RGB", 1280, 800)

  # Move both to the EXACT same screen coordinates (X, Y)
  # This stacks "RGB" directly on top of "disp"
  cv2.moveWindow("disp", 100, 100)
  cv2.moveWindow("RGB", 100, 100)

  index = 0
  points = [(0,0,0), (0,0,0)]

  cv2.setMouseCallback("disp", mouse_callback)

  def get_length(p1):
    z1 = p1[0][2]
    x_mm1 = (p1[0][0] - cx) * z1 / fx
    y_mm1 = (p1[0][1] - cy) * z1 / fy

    z2 = p1[1][2]
    x_mm2 = (p1[1][0] - cx) * z2 / fx
    y_mm2 = (p1[1][1] - cy) * z2 / fy
    x_mm1, x_mm2 = np.int64(x_mm1), np.int64(x_mm2)
    y_mm1, y_mm2 = np.int64(y_mm1), np.int64(y_mm2)
    length = np.sqrt(abs(x_mm1 - x_mm2)**2 + abs(y_mm1 - y_mm2)**2 + (z1 - z2)**2)
    height = abs(y_mm1 - y_mm2)
    length = f'Length is {length/10}'
    height = f'Height is {height/10}'
    return length, height 

  while True:
    z = frame_depth[mouse_y, mouse_x]
    if z > 0:
      x_mm = (mouse_x - cx) * z / fx
      y_mm = (mouse_y - cy) * z / fy
      label = f"X: {int(x_mm/10)} Y: {int(y_mm/10)} Z: {int(z/10)} in cm"
    else:
      label = "Z: Invalid (Too close or low texture)"
      color = (0, 0, 255) # Red for invalid
    length, height = get_length(points)
    label += ' ' + length
    # UI Overlay
    disp_frame = cv2.normalize(frame_depth, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
    disp_frame = cv2.applyColorMap(disp_frame, cv2.COLORMAP_JET)
    cv2.putText(disp_frame, label, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    label = height
    cv2.putText(disp_frame, label, (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.circle(disp_frame, (mouse_x, mouse_y), 2, (255, 255, 255), -1)
    for point in points:
      cv2.circle(disp_frame, (point[0], point[1]), 2, (255, 255, 255), -1)

    cv2.imshow("disp", disp_frame)
    cv2.imshow('RGB', frame_rgb)
    key = cv2.waitKey(1)
    if key == ord('q'):
      break
    elif key == ord('e'):
      points[index] = (mouse_x, mouse_y, z)
      index += 1
      index %= 2

if __name__ == '__main__':
  counter = 0
  while True:
    try:
      frame_depth, frame_rgb, intrinsics = get_data(f'Iceberg{counter}/')
      run_ts(frame_depth, frame_rgb, intrinsics)
      counter += 1
    except:
      break