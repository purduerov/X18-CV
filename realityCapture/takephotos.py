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


cap = cv2.VideoCapture(0)

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