import cv2
from ultralytics import YOLO

# 1. Load your original model
model = YOLO(r'best_v2.pt')

# 2. Setup Laptop Webcam
# '0' is usually the built-in webcam. Try '1' or '2' if you have an external USB cam.
cap = cv2.VideoCapture(1)
#cap = cv2.VideoCapture("rtsp://192.168.1.51:8554/camera_1")


if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

print("MATE ROV: Webcam Mode Initialized. Press 'q' to quit.")

while True:
    # Capture frame-by-frame from webcam
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame.")
        break

    # 3. Run YOLO inference 
    # Increased confidence to 0.85 to reduce false positives
    results = model(frame, conf=0.75, verbose=False, classes=[0])  # Only detect class 0 (Green Crabs)
    r = results[0]

    # 4. Logic & Terminal Output
    count_green = 0
    if len(r.boxes) > 0:
        # Count only Green Crabs (Class 0)
        mask = (r.boxes.cls == 0)
        #.sum().item()
        r.boxes = r.boxes[mask]
    
    # Print result to terminal
        print(f"Current Green Crab Count: {int(mask.sum().item())}")

    # 5. Visualization (Minimal)
    annotated_frame = r.plot()
    
    cv2.imshow("Webcam Test - Green Crabs Only", annotated_frame)

    # Break loop on 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup

cap.release()
cv2.destroyAllWindows()