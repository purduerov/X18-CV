import cv2
import numpy as np
import glob

file = open('data/train/pos/info.dat', 'w')

images = glob.glob("data/train/pos/img/*")
for fname in images:
    img = cv2.imread(fname)

    drawing = False
    ix,iy = -1, -1
    ex,ey = -1, -1

    def draw_rectangle(event, x, y, flags, param):
        global ix, iy, ex, ey, drawing, img
        if event == cv2.EVENT_LBUTTONDOWN:
            drawing = True
            ix = x
            iy = y
        elif event == cv2.EVENT_LBUTTONUP:
            drawing = False
            ex = x
            ey = y
            cv2.rectangle(img, (ix, iy),(x, y),(0, 255, 0),5)
            cv2.imshow("Rectangle Window", img)

    # Create a window and bind the function to window
    cv2.namedWindow("Rectangle Window")

    # Connect the mouse button to our callback function
    cv2.setMouseCallback("Rectangle Window", draw_rectangle)

    cv2.imshow("Rectangle Window", img)

    cv2.waitKey()
    
    print(fname[fname.index("img"):], ix, iy, ex, ey)
    file.write(f'{fname[fname.index("img"):]} 1 {ix} {iy} {ex} {ey}')

cv2.destroyAllWindows()

file.close()