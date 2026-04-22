import cv2
import os

# Paths to your data
image_folder = r'C:\Users\User\ROV\X18-CV\Crab_Detection\YOLO_Crab_Detection\data\images\train'
label_folder = r'C:\Users\User\ROV\X18-CV\Crab_Detection\YOLO_Crab_Detection\data\labels\train'

# Class names mapping (must match your new YAML)
class_names = {0: 'Green Crab', 1: 'Rock Crab', 2: 'Jonah Crab'}
colors = {0: (0, 255, 0), 1: (255, 0, 0), 2: (0, 0, 255)} # G, B, R

def verify_labels(img_name):
    img_path = os.path.join(image_folder, img_name)
    label_path = os.path.join(label_folder, img_name.replace('.jpg', '.txt').replace('.JPG', '.txt'))
    
    if not os.path.exists(label_path):
        print(f"No label found for {img_name}")
        return

    img = cv2.imread(img_path)
    h, w, _ = img.shape

    with open(label_path, 'r') as f:
        for line in f:
            cls, x_c, y_c, wb, hb = map(float, line.split())
            
            # Convert normalized to pixel coordinates
            x1 = int((x_c - wb/2) * w)
            y1 = int((y_c - hb/2) * h)
            x2 = int((x_c + wb/2) * w)
            y2 = int((y_c + hb/2) * h)

            # Draw
            color = colors.get(int(cls), (255, 255, 255))
            cv2.rectangle(img, (x1, y1), (x2, y2), color, 3)
            cv2.putText(img, class_names.get(int(cls), "Unknown"), (x1, y1 - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

    # Show result (Resizable window)
    cv2.namedWindow("Verify", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Verify", 1280, 720)
    cv2.imshow("Verify", img)
    cv2.waitKey(0)

# Test on first 5 images
images = [f for f in os.listdir(image_folder) if f.endswith(('.jpg', '.JPG'))]
for i in range(5):
    verify_labels(images[i])

cv2.destroyAllWindows()