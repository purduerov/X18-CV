from ultralytics import YOLO
import cv2
import os
import color_reduction

img_path1 = r"C:\Users\User\ROV\X18-CV\Crab_Detection\Competition_Image.png"
img_path2 = r"C:\Users\User\ROV\X18-CV\Crab_Detection\reduced_k2.jpg"
img_path3 = r"C:\Users\User\ROV\X18-CV\Crab_Detection\reduced_k4.jpg"
img_path4 = r"C:\Users\User\ROV\X18-CV\Crab_Detection\reduced_k8.jpg"

color_reduction.stress_test_image

# 1. Load model
model = YOLO('best.pt')

# 2. Run prediction with 'visualize=True'
# This will save every layer's "thought process" into a folder
# results = model.predict(source=r'C:\Users\User\ROV\X18-CV\Crab_Detection\GreenCrab.jpg', visualize=True, save=True)
results = model.predict(source=img_path1, save=True)
results = model.predict(source=img_path2, save=True)
results = model.predict(source=img_path3, save=True)
results = model.predict(source=img_path4, save=True)


print(f"Feature maps saved to: {os.path.join(os.getcwd(), 'runs/detect/predict')}")