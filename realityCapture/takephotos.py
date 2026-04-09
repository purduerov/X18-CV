'''

import cv2
import boto3
import time

import requests


# AWS config
BUCKET_NAME = "3d-reconstruction-cv"
REGION = "us-east-2"  # change if needed

s3 = boto3.client("s3")

image_urls = []

def send_to_server(url):
    try:
        res = requests.post(
            "http://localhost:3000/api/photos",
            json={"url": url}
        )
        print("Sent to server:", res.json())

    except Exception as e:
        print("Error sending to server:", e)

def upload_to_s3(filepath, key):
    s3.upload_file(
        filepath,
        BUCKET_NAME,
        key,
        ExtraArgs={"ContentType": "image/jpeg"}
    )

    # public URL format
    url = f"https://{BUCKET_NAME}.s3.{REGION}.amazonaws.com/{key}"
    return url

#cap = cv2.VideoCapture(0)
cap = cv2.VideoCapture("rtsp://192.168.1.51:8554/camera_3")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    cv2.imshow("Camera", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord('c'):
        filename = f"capture_{int(time.time())}.jpg"
        cv2.imwrite(filename, frame)

        s3_key = f"runs/run_{int(time.time())}/{filename}"
        public_url = upload_to_s3(filename, s3_key)

        image_urls.append(public_url)

        send_to_server(public_url)  

        print("Uploaded:", public_url)

    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

print("All URLs:", image_urls)
'''

import cv2
import time
import json
import os

# =========================
# OFFLINE CONFIG
# =========================
SAVE_DIR = "offline_captures"
METADATA_FILE = "offline_images.json"

# create folder if it doesn't exist
os.makedirs(SAVE_DIR, exist_ok=True)

# in-memory list
offline_images = []

# load existing images if file exists
if os.path.exists(METADATA_FILE):
    with open(METADATA_FILE, "r") as f:
        try:
            offline_images = json.load(f)
        except:
            offline_images = []

# =========================
# CAMERA
# =========================
#cap = cv2.VideoCapture("rtsp://192.168.1.51:8554/camera_3")
cap = cv2.VideoCapture(1)

# create ONE run id (important)
run_id = int(time.time())

while True:
    ret, frame = cap.read()
    if not ret:
        break

    cv2.imshow("Camera", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord('c'):
        timestamp = int(time.time())

        filename = f"capture_{timestamp}.jpg"
        filepath = os.path.join(SAVE_DIR, filename)

        # save image
        cv2.imwrite(filepath, frame)

        # create structured record
        record = {
            "filename": filename,
            "filepath": filepath,
            "run_id": run_id,
            "timestamp": timestamp
        }

        # store in memory
        offline_images.append(record)

        # persist to file
        with open(METADATA_FILE, "w") as f:
            json.dump(offline_images, f, indent=2)

        print("Saved locally:", filepath)

    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

print("\n=== SESSION COMPLETE ===")
print("Total images:", len(offline_images))
print("Saved in:", SAVE_DIR)
print("Metadata file:", METADATA_FILE)