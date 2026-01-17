import cv2
from ultralytics import YOLO

# 1. Load your trained model
# Ensure 'best.pt' is in the same directory or provide the full path
model = YOLO(r'Crab_Detection\best.pt')

# 2. Access the webcam
# '0' is usually the default integrated laptop camera
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

print("Press 'q' to quit the video stream.")

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to grab frame.")
        break

    # 3. Run YOLOv8 inference on the frame
    # We set stream=True for better performance with video
    # .predict() is used for live inference
    results = model.predict(source=frame, conf=0.5, show=False, stream=True)

    for r in results:
        # 4. Count the specific Invasive Crab (Class 0)
        # Assuming 0: GreenCrab, 1: RockCrab, 2: JonahCrab
        count_green = (r.boxes.cls == 0).sum().item()

        # 5. Visualize the detections
        # This draws the boxes and labels on the frame
        annotated_frame = r.plot()

        # 6. Add the Count Overlay (Competition Requirement)
        cv2.putText(
            annotated_frame, 
            f"Green Crabs: {int(count_green)}", 
            (20, 50), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            1, 
            (0, 255, 0), 
            2
        )

        # Display the resulting frame
        cv2.imshow('MATE ROV - Crab Detection Test', annotated_frame)

    # 7. Exit logic: Press 'q' on the keyboard to stop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture and close windows
cap.release()
cv2.destroyAllWindows()