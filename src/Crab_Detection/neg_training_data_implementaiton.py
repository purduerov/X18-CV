import os
import shutil
import random

def integrate_negatives(neg_source_dir, dataset_base_dir, split_ratio=0.8):
    """
    Moves negative images into the YOLO dataset and creates empty label files.
    """
    # Define target paths based on your existing script
    train_img_dir = os.path.join(dataset_base_dir, 'images', 'train')
    val_img_dir = os.path.join(dataset_base_dir, 'images', 'val')
    train_lbl_dir = os.path.join(dataset_base_dir, 'labels', 'train')
    val_lbl_dir = os.path.join(dataset_base_dir, 'labels', 'val')

    # Get all negative images from your collection folder
    neg_files = [f for f in os.listdir(neg_source_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    random.shuffle(neg_files)

    print(f"Integrating {len(neg_files)} negative images...")

    for i, filename in enumerate(neg_files):
        # Determine split
        is_train = i < (len(neg_files) * split_ratio)
        
        target_img_folder = train_img_dir if is_train else val_img_dir
        target_lbl_folder = train_lbl_dir if is_train else val_lbl_dir

        # 1. Copy the Image
        src_path = os.path.join(neg_source_dir, filename)
        dst_path = os.path.join(target_img_folder, filename)
        shutil.copy(src_path, dst_path)

        # 2. Create the EMPTY Label File
        # Change extension to .txt (e.g., neg_1.jpg -> neg_1.txt)
        label_filename = os.path.splitext(filename)[0] + ".txt"
        with open(os.path.join(target_lbl_folder, label_filename), 'w') as f:
            pass # Creating an empty file tells YOLO "This is background"

    print("Success: Negatives integrated with empty labels.")

# --- EXECUTION ---
# Change 'negatives' to the folder where you saved your 80 OAK-D snapshots
integrate_negatives('negatives', 'YOLO_Crab_Detection/data')