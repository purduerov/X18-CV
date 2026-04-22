import cv2 as cv
import numpy as np
import glob

criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((6 * 8, 3), np.float32)
objp[:, :2] = np.mgrid[0:8, 0:6].T.reshape(-1, 2)
# Arrays to store object points and image points from all the images.
objpoints = []  # 3d point in real world space
imgpoints = []  # 2d points in image plane.
images = glob.glob("data/calibration/*.jpg")
for fname in images:
    img = cv.imread(fname)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    # Find the chess board cornersq
    ret, corners = cv.findChessboardCorners(gray, (8, 6), None)
    # If found, add object points, image points (after refining them)
    if ret:
        print("reading" + fname)
        objpoints.append(objp)
        corners2 = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        imgpoints.append(corners2)
        # Draw and display the corners
        cv.drawChessboardCorners(img, (8, 6), corners2, ret)
        cv.imshow("img", img)
        cv.waitKey(100)
        print("hang?")
    else:
        print("failed to find corner")

ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(
    objpoints, imgpoints, gray.shape[::-1], None, None
)

print(type(ret))
print(type(mtx))
print(type(dist))
print(type(rvecs))

out_file = open("calibration_res.txt", "w")


out_file.write("ret=" + str(ret) + "\n")
out_file.write("mtx=" + str(mtx) + "\n")
out_file.write("dist=" + str(dist) + "\n")
out_file.write("rvecs=" + str(rvecs) + "\n")
out_file.write("tvecs=" + str(tvecs) + "\n")

out_file.close()