import cv2
import numpy as np

def get_data(dir):
  frame_rgb = cv2.imread('test1.jpg')
  return frame_rgb

mouse_x, mouse_y = 320, 200
def rgb_mouse_callback(event, x, y, flags, param):
      global mouse_x, mouse_y
      if event == cv2.EVENT_MOUSEMOVE:
          mouse_x, mouse_y = x, y



def run_ts(frame_depth):
  global mouse_x, mouse_y
  
  cv2.namedWindow("RGB", cv2.WINDOW_NORMAL)

  # Set identical sizes
  cv2.resizeWindow("RGB", 1280, 800)

  # Move both to the EXACT same screen coordinates (X, Y)
  # This stacks "RGB" directly on top of "disp"
  cv2.moveWindow("RGB", 100, 100)

  index = 0
  points = [(0,0,0), (0,0,0)]

  cv2.setMouseCallback("RGB", rgb_mouse_callback)


  while True:
    frame_cpy = frame_rgb.copy()
    label = f'Mouse x: {mouse_x}, Mouse y: {mouse_y}'
    cv2.putText(frame_cpy, label, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
    cv2.circle(frame_cpy, (mouse_x, mouse_y), 0, (0, 0, 255), -1)
    cv2.imshow('RGB', frame_cpy)
    key = cv2.waitKey(1) & 0xFF

    if key == 255:
      continue
    
    if key == ord('q'):
      break
    elif key == 82:
      mouse_y -= 1
    elif key == 84:
      mouse_y += 1
    elif key == 81:
      mouse_x -= 1
    elif key == 83:
      mouse_x += 1
    elif key == ord('e'):
      points[index] = (mouse_x, mouse_y, z)
      index += 1
      index %= 2

if __name__ == '__main__':
  counter = 0
  while True:
    try:
      frame_rgb = get_data(f'Iceberg{counter}/')
      run_ts(frame_rgb)
      break
    except:
      break