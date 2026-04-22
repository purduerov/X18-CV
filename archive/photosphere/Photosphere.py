import numpy as np
import cv2
# Initialize the stitcher based on OpenCV version
stitcher = cv2.Stitcher_create() if int(cv2.__version__.split('.')[0]) >= 4 else cv2.createStitcher()
# Set up video capture
#cap = cv2.VideoCapture(0)q
#cap = cv2.VideoCapture("/Users/aranpandey/Downloads/underwatertest_wdY1aPfW.mp4")
cap = cv2.VideoCapture(0)
frames = []
counter = 0
capture_interval = 20  # Modify this value to change the frame capture interval
if not cap.isOpened():
    print("Failed to open camera. Exiting.")
    exit()
print("Press 'q' to exit the capture loop.")
while True:
    counter += 1
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture frame. Exiting.")
        break
    # Resize the frame for faster processing and consistency
    frame = cv2.resize(frame, (1280, 720))
    # Display the frame
    cv2.imshow('Live Camera Feed', frame)
    # Capture every nth frame for stitching
    if counter % capture_interval == 0:
        frames.append(frame)
        print(f"Captured frame {len(frames)}")
    # Exit when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
# Release the capture and close any open windows
cap.release()
cv2.destroyAllWindows()
# Check if we have enough frames to perform stitching
if len(frames) < 2:
    print("Not enough frames captured for stitching.")
else:
    print(f"Number of frames captured: {len(frames)}")
    # Perform the stitching process
    status, stitched = stitcher.stitch(frames)
    if status == cv2.Stitcher_OK:
        print("Stitching completed successfully.")
        # Show the stitched image to confirm it's correctly stitched
        cv2.imshow('Stitched Image', stitched)
        cv2.imwrite('stitch.jpg', stitched, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
        print("Saved stitched image as stitch.jpg")

        cv2.waitKey(0)  # Wait for a key press to proceed
        cv2.destroyAllWindows()
        # Perform a spherical warp for a basic photosphere effect
        h, w = stitched.shape[:2]
        focal_length = 700  # Adjust this parameter to control the warp
        # Create a more refined camera matrix
        K = np.array([[focal_length, 0, w / 2],
                      [0, focal_length, h / 2],
                      [0, 0, 1]])  # Camera matrix
        # Warp to spherical coordinates, verify shape and camera matrix
        stitched_sphere = cv2.warpPerspective(stitched, K, (w, h),
                                              flags=cv2.WARP_INVERSE_MAP | cv2.INTER_LINEAR)
        # Show the warped spherical image
        cv2.imshow('Photosphere', stitched_sphere)
        cv2.imwrite('stitch.png', stitched_sphere)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    elif status == cv2.Stitcher_ERR_NEED_MORE_IMGS:
        print("Error: Not enough images to perform stitching.")
    elif status == cv2.Stitcher_ERR_HOMOGRAPHY_EST_FAIL:
        print("Error: Homography estimation failed. Not enough overlapping features between images.")
    elif status == cv2.Stitcher_ERR_CAMERA_PARAMS_ADJUST_FAIL:
        print("Error: Adjusting camera parameters (e.g., focal length, distortion) failed during stitching.")
    else:
        print(f"Stitching failed. Unknown error with status code: {status}")
stitched = cv2.imread('stitch.jpg')