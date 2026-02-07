from ultralytics import YOLO
import cv2

model = YOLO(r"best.pt")

image_path = r"C:\Users\User\ROV\X18-CV\Crab_Detection\Competition_Image.png"

results = model.predict(
    source=image_path,
    conf=0.75,
    imgsz=640,
    save=False
)

annotated_frame = results[0].plot()

cv2.imshow("Crab Detection Fram Test", annotated_frame)

cv2.waitKey(0)
cv2.destroyAllWindows