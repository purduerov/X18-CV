import cv2

# Open the default camera (usually camera index 0)
cap = cv2.VideoCapture(1)

# Check if the camera opened successfully
if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

# Counter for captured images
counter = 0

while True:
    # Read a frame from the camera
    ret, frame = cap.read()

    # Display the frame
    cv2.imshow('Camera', frame)

    # Wait for a key press (here, wait for 1 millisecond)
    key = cv2.waitKey(1)

    # Check if the pressed key is the ESC key (27)
    if key == 27:
        break
    elif key == ord('s'):
        # Save the current frame as an image
        image_name = f'captured_image_{counter}.jpg'
        cv2.imwrite(image_name, frame)
        print(f"Image {image_name} saved.")
        counter += 1

# Release the camera and close the window
cap.release()
cv2.destroyAllWindows()
