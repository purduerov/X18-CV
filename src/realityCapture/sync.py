import boto3
import requests
import json
import os
import time

# =========================
# CONFIG
# =========================
BUCKET_NAME = "3d-reconstruction-cv"
REGION = "us-east-2"

METADATA_FILE = "offline_images.json"
SERVER_URL = "http://localhost:3000/api/photos"

s3 = boto3.client("s3")

# =========================
# LOAD METADATA
# =========================
if not os.path.exists(METADATA_FILE):
    print("No offline_images.json found")
    exit()

with open(METADATA_FILE, "r") as f:
    images = json.load(f)

print(f"Loaded {len(images)} images")

# =========================
# SYNC LOOP
# =========================
uploaded_count = 0


for img in images:
    # skip already uploaded images
    if img.get("sent_to_model"):
        continue

    filepath = img["filepath"]
    filename = img["filename"]
    run_id = img["run_id"]

    if not os.path.exists(filepath):
        print("File missing:", filepath)
        continue

    try:
        # -------- Upload to S3 --------
        s3_key = f"runs/run_{run_id}/{filename}"

        s3.upload_file(
            filepath,
            BUCKET_NAME,
            s3_key,
            ExtraArgs={"ContentType": "image/jpeg"}
        )

        public_url = f"https://{BUCKET_NAME}.s3.{REGION}.amazonaws.com/{s3_key}"

        print("Uploaded to S3:", public_url)

        # -------- Send to server --------
        res = requests.post(
            SERVER_URL,
            json={"url": public_url}
        )

        print("Sent to server:", res.json())

        # -------- Mark as uploaded --------
        img["sent_to_model"] = True
        img["s3_url"] = public_url

        uploaded_count += 1

        # small delay (prevents spam / throttling)
        time.sleep(0.2)

    except Exception as e:
        print("Error processing", filename, ":", e)

# =========================
# SAVE UPDATED METADATA
# =========================
with open(METADATA_FILE, "w") as f:
    json.dump(images, f, indent=2)

print("\n=== SYNC COMPLETE ===")
print("Uploaded:", uploaded_count)