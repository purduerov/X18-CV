# Convert data into something readable

# Create a mask around the crab
# SAM - Segement Anything
# Take the background out

import cv2
import numpy as np
import os
import random
from PIL import Image

# --- GLOBAL SETUP (outside any function) ---
BACKGROUND_DIR = 'backgrounds' # Must exist and contain JPGs/PNGs
if not os.path.exists(BACKGROUND_DIR):
    print(f"WARNING: '{BACKGROUND_DIR}' not found. Please create it and add background images.")
# Get a list of all background file paths
BACKGROUND_PATHS = [os.path.join(BACKGROUND_DIR, f) for f in os.listdir(BACKGROUND_DIR) if f.lower().endswith(('.jpg', '.png'))]
if not BACKGROUND_PATHS:
    print("WARNING: No background images found. Using default canvas.")
# Define the canvas size (simulating the ROV camera view)
CANVAS_SIZE = 1024
# Define the number of final composite images to generate
NUM_COMPOSITE_IMAGES = 1200

# Define class IDs: The ID corresponds to the index in your names array in config.yaml
CLASS_IDS = {
    'GreenCrab': 0,
    'RockCrab': 1,
    'JonahCrab': 2
}

# --- Utility Function to Handle Rotation and Bounding Box Calculation ---
def calculate_rotated_bbox(x_min, y_min, w, h, angle_degrees, canvas_w, canvas_h):
    """
    Calculates the new axis-aligned bounding box (x_center, y_center, width, height)
    for an object placed at (x_min, y_min) and rotated, relative to the canvas.
    """

    # 1. Define the four corners of the unrotated box relative to the canvas
    corners = np.array([
        [x_min, y_min],        # Top-Left
        [x_min + w, y_min],    # Top-Right
        [x_min, y_min + h],    # Bottom-Left
        [x_min + w, y_min + h] # Bottom-Right
    ])

    # 2. Get the center of the unrotated object for rotation
    cx = x_min + w / 2
    cy = y_min + h / 2

    # 3. Apply Rotation (Standard OpenCV rotation is often simpler than manual matrix for 2D)
    angle_rad = np.deg2rad(angle_degrees)
    cos_a, sin_a = np.cos(angle_rad), np.sin(angle_rad)

    # Calculate rotated corners relative to the canvas center
    rotated_corners = []
    for x, y in corners:
        # Translate point to origin
        temp_x = x - cx
        temp_y = y - cy

        # Rotate point
        new_x = temp_x * cos_a - temp_y * sin_a
        new_y = temp_x * sin_a + temp_y * cos_a

        # Translate point back
        rotated_corners.append([new_x + cx, new_y + cy])

    rotated_corners = np.array(rotated_corners)

    # 4. Find the Axis-Aligned Bounding Box (AABB)
    x_coords = rotated_corners[:, 0]
    y_coords = rotated_corners[:, 1]

    x_min_new = np.min(x_coords)
    x_max_new = np.max(x_coords)
    y_min_new = np.min(y_coords)
    y_max_new = np.max(y_coords)

    # 5. Calculate Center, Width, and Height (in pixels)
    bbox_w = x_max_new - x_min_new
    bbox_h = y_max_new - y_min_new
    bbox_cx = x_min_new + bbox_w / 2
    bbox_cy = y_min_new + bbox_h / 2

    # 6. Normalize (YOLO Format)
    yolo_x_center = bbox_cx / canvas_w
    yolo_y_center = bbox_cy / canvas_h
    yolo_w = bbox_w / canvas_w
    yolo_h = bbox_h / canvas_h

    # Ensure coordinates are within [0.0, 1.0] and return
    return [yolo_x_center, yolo_y_center, yolo_w, yolo_h]

# --- Main Composition Function ---
def generate_yolo_dataset(crab_assets, output_base_dir):

    # 1. Setup Directories
    img_dir_train = os.path.join(output_base_dir, 'images', 'train')
    lbl_dir_train = os.path.join(output_base_dir, 'labels', 'train')
    img_dir_val = os.path.join(output_base_dir, 'images', 'val')
    lbl_dir_val = os.path.join(output_base_dir, 'labels', 'val')

    for d in [img_dir_train, lbl_dir_train, img_dir_val, lbl_dir_val]:
        os.makedirs(d, exist_ok=True)

    all_crab_names = list(crab_assets.keys())

    for i in range(NUM_COMPOSITE_IMAGES):

        # Determine if this image is for training (80%) or validation (20%)
        is_train = random.random() < 0.8
        img_dir = img_dir_train if is_train else img_dir_val
        lbl_dir = lbl_dir_train if is_train else lbl_dir_val

        # --- FIX 1: DYNAMIC UNDERWATER CANVAS ---
        canvas = load_random_background(CANVAS_SIZE)

        yolo_labels = []
        # List to track [x_min, y_min, x_max, y_max] of placed crabs (AABB pixels)
        placed_boxes = []

        num_crabs = random.randint(5, 15)
        MAX_PLACEMENT_ATTEMPTS = 50

        for _ in range(num_crabs):

            # 2. Randomly select crab type and its corresponding asset image
            crab_name = random.choice(all_crab_names)
            crab_img_path = random.choice(crab_assets[crab_name])
            crab_img = cv2.imread(crab_img_path, cv2.IMREAD_UNCHANGED)

            # 3. Apply Final Transforms and Placement

            target_size = random.randint(100, 300)
            crab_resized = cv2.resize(crab_img, (target_size, target_size),
                                      interpolation=cv2.INTER_AREA)

            # --- FIX 2: NON-OVERLAP PLACEMENT LOGIC ---
            attempt = 0
            placed = False
            x_min, y_min = 0, 0
            rotation_angle = 0 # Define outside loop

            while not placed and attempt < MAX_PLACEMENT_ATTEMPTS:

                # Random rotation and placement coordinates for the attempt
                rotation_angle = random.uniform(0, 360)
                x_min_try = random.randint(0, CANVAS_SIZE - target_size)
                y_min_try = random.randint(0, CANVAS_SIZE - target_size)

                # Calculate the AABB for the overlap check using the simple, unrotated dimensions
                # NOTE: This assumes target_size is the maximum dimension of the rotated crab.
                current_box = (x_min_try, y_min_try, x_min_try + target_size, y_min_try + target_size)

                if not check_overlap(current_box, placed_boxes):
                    # No overlap found! Lock in position and angle.
                    x_min, y_min = x_min_try, y_min_try
                    placed = True

                attempt += 1

            if not placed:
                # If max attempts reached, move to the next crab
                continue

                # 4. Paste and Rotate (Only runs if a non-overlapping spot was found)
            try:
                # Convert the OpenCV BGR resized image to PIL RGB format
                crab_pil = Image.fromarray(cv2.cvtColor(crab_resized, cv2.COLOR_BGR2RGB))

                # Apply rotation
                crab_rotated_pil = crab_pil.rotate(rotation_angle,
                                                   resample=Image.Resampling.BILINEAR,
                                                   expand=False)

                # Convert back to OpenCV BGR format
                crab_rotated_cv = cv2.cvtColor(np.array(crab_rotated_pil), cv2.COLOR_RGB2BGR)

                # 1. Define the near-black color range (BGR: 0-10 for all channels)
                lower_black = np.array([0, 0, 0])
                upper_black = np.array([10, 10, 10])

                # 2. Create a mask of the pixels that are black (the corners)
                black_mask = cv2.inRange(crab_rotated_cv, lower_black, upper_black)

                # 3. Get the corresponding background color from the canvas
                # The background color is not a single value due to caustics and texture.
                # We will use the average color of the canvas area *underneath* the patch.
                h_rot, w_rot, _ = crab_rotated_cv.shape
                background_patch = canvas[y_min:y_min + h_rot, x_min:x_min + w_rot]

                # 4. Use the background patch to fill the black mask area
                # We use the cv2.bitwise_not(black_mask) to get the crab area mask
                # And cv2.bitwise_and(black_mask) to get the corner area mask
                # The final operation places the background patch where the black pixels were:
                crab_rotated_cv = cv2.bitwise_and(crab_rotated_cv, crab_rotated_cv, mask=cv2.bitwise_not(black_mask))
                background_patch = cv2.bitwise_and(background_patch, background_patch, mask=black_mask)
                crab_rotated_cv = cv2.add(crab_rotated_cv, background_patch)

                # Get dimensions of the actual image after rotation (AABB)
                h_rot, w_rot, _ = crab_rotated_cv.shape

                # Update the paste area coordinates
                x_end = x_min + w_rot
                y_end = y_min + h_rot

                # Final boundary check (should rarely happen with good x_min/y_min logic)
                if x_end > CANVAS_SIZE or y_end > CANVAS_SIZE:
                    continue

                # DIRECT PASTE: Overwrite the background pixels in the canvas
                canvas[y_min:y_end, x_min:x_end] = crab_rotated_cv

                # --- FIX 3: RECORDING THE FINAL, CORRECT BOX ---
                # The final bounding box on the canvas
                final_box = (x_min, y_min, x_min + w_rot, y_min + h_rot)
                placed_boxes.append(final_box)

            except Exception as e:
                print(f"Error during rotation/paste: {e}")
                continue # Skip this crab and move to the next iteration

            # 5. Calculate and Record Bounding Box (YOLO FORMAT)

            # Use the actual rotated dimensions (w_rot, h_rot) for the normalized box!
            w_box, h_box = w_rot, h_rot

            # Center calculation based on placement (x_min, y_min) and rotated size
            x_center = (x_min + w_box / 2) / CANVAS_SIZE
            y_center = (y_min + h_box / 2) / CANVAS_SIZE
            w_norm = w_box / CANVAS_SIZE
            h_norm = h_box / CANVAS_SIZE

            # Ensure normalization clips to 0.0-1.0 to avoid YOLO training errors
            x_center = np.clip(x_center, 0.0, 1.0)
            y_center = np.clip(y_center, 0.0, 1.0)
            w_norm = np.clip(w_norm, 0.0, 1.0)
            h_norm = np.clip(h_norm, 0.0, 1.0)


            class_id = CLASS_IDS[crab_name]
            label_line = f"{class_id} {x_center:.6f} {y_center:.6f} {w_norm:.6f} {h_norm:.6f}\n"
            yolo_labels.append(label_line)

        # 6. Save the composite image and label file
        filename = f'comp_{i+1:04d}'
        cv2.imwrite(os.path.join(img_dir, f'{filename}.jpg'), canvas)

        with open(os.path.join(lbl_dir, f'{filename}.txt'), 'w') as f:
            f.writelines(yolo_labels)

        if (i + 1) % 100 == 0 or (i + 1) == NUM_COMPOSITE_IMAGES:
            print(f" -> Generated {i+1} / {NUM_COMPOSITE_IMAGES} composite images.")

def check_overlap(new_box, existing_boxes, min_padding=20):
    """Checks if a new axis-aligned bounding box overlaps with existing ones."""

    # new_box format: (x_min, y_min, x_max, y_max)
    nx_min, ny_min, nx_max, ny_max = new_box

    for bx_min, by_min, bx_max, by_max in existing_boxes:
        # Check for non-overlap condition first (faster)
        # If one rectangle is on the left side of the other
        if nx_max <= bx_min - min_padding or nx_min >= bx_max + min_padding:
            continue
        # If one rectangle is above the other
        if ny_max <= by_min - min_padding or ny_min >= by_max + min_padding:
            continue

        # If non-overlap conditions fail, they must overlap
        return True
    return False

def generate_underwater_canvas(size):
    """
    Generates a dynamic canvas simulating a bright, tiled pool background
    with pronounced water caustics.
    """

    # 1. Base Color (Bright Pool Blue/Cyan BGR)
    # Using brighter blues and greens is key for a less 'wooden' look.
    base_color = np.array([200, 180, 50], dtype=np.uint8) # BGR: Bright Blue/Cyan
    canvas = np.full((size, size, 3), fill_value=base_color.tolist(), dtype=np.uint8)

    # 2. Add Subtle Tile Grid (If the pool tank has visible tiling)
    # Use a very thin, light line to simulate grout.
    grout_color = np.array([180, 160, 40], dtype=np.uint8).tolist()
    tile_spacing = random.randint(40, 80)

    for y in range(0, size, tile_spacing):
        cv2.line(canvas, (0, y), (size, y), grout_color, 1)
    for x in range(0, size, tile_spacing):
        cv2.line(canvas, (x, 0), (x, size), grout_color, 1)

    # 3. Generating Caustics (Wavy Light Patterns)
    # Caustics are more effective than simple Gaussian noise for lighting variation.

    # Create a base noise layer (e.g., Perlin/Simplex noise simulation using NumPy)
    # For simplicity without external libraries, we use multiple blurred random fields:
    caustic_mask = np.zeros((size, size), dtype=np.float32)

    for _ in range(3): # Blend a few layers for a more organic look
        noise = np.random.normal(0, 10, (size, size)).astype(np.float32)
        # Apply a strong blur to simulate the wave movement
        noise = cv2.GaussianBlur(noise, (0, 0), sigmaX=random.uniform(20, 40))
        caustic_mask += noise

    # Rescale and shift the mask to be a brightness multiplier centered around 1.0
    # Range will be approximately [0.7, 1.3] (dimming and brightening)
    caustic_mask = (caustic_mask - caustic_mask.min()) / (caustic_mask.max() - caustic_mask.min())
    caustic_mask = caustic_mask * random.uniform(0.4, 0.7) + random.uniform(0.7, 0.9)

    # 4. Apply Caustics to Canvas
    canvas_f = canvas.astype(np.float32)
    # Apply the 2D mask to all 3 color channels
    canvas_f = canvas_f * caustic_mask[:, :, np.newaxis]

    # Add a final random exposure shift to simulate light changes
    canvas_f += random.uniform(-10, 10)

    return np.clip(canvas_f, 0, 255).astype(np.uint8)

def apply_color_shift(image, factor=0.1):
    """
    Applies a blue/green shift characteristic of underwater environments to an image.
    This simulates color absorption in water.
    """
    img_f = image.astype(np.float32)

    # Increase Blue and Green channels, decrease Red channel (BGR)
    # Factor determines the maximum boost/reduction
    b_boost = np.random.uniform(1.0, 1.0 + factor)
    g_boost = np.random.uniform(1.0, 1.0 + factor)
    r_reduce = np.random.uniform(1.0 - factor, 1.0)

    # Apply the shift to the channels
    img_f[:, :, 0] *= b_boost # Blue Channel
    img_f[:, :, 1] *= g_boost # Green Channel
    img_f[:, :, 2] *= r_reduce # Red Channel

    # Clip values and convert back to 8-bit
    return np.clip(img_f, 0, 255).astype(np.uint8)

def apply_haze_and_fog(image, density_range=(0.0, 0.2)):
    """
    Simulates water turbidity/fog by blending the image with a light color.
    """
    # Density determines how much of the fog color is mixed in
    density = np.random.uniform(*density_range)

    # Light blue/white color to simulate particles in the water column (BGR)
    fog_color = np.array([200, 220, 230], dtype=np.uint8)

    # Create an overlay layer of the fog color
    overlay = np.full(image.shape, fog_color, dtype=np.uint8)

    # Blend the image and the overlay (alpha is 1 - density)
    # The result is: image * (1 - density) + overlay * density
    return cv2.addWeighted(image, 1 - density, overlay, density, 0)

def load_random_background(size):
    """Loads a random background image and applies environmental augmentations."""

    # 1. Fallback Check
    if not BACKGROUND_PATHS:
        # Fallback to a simple blue canvas if no images are available
        # Using a mid-range pool blue/gray BGR
        return np.full((size, size, 3), fill_value=[150, 100, 50], dtype=np.uint8)

    # 2. Load and Resize
    bg_path = random.choice(BACKGROUND_PATHS)
    bg_img = cv2.imread(bg_path)

    # Handle loading errors if file is corrupted
    if bg_img is None:
        print(f"Error reading background image: {bg_path}. Using fallback.")
        return np.full((size, size, 3), fill_value=[150, 100, 50], dtype=np.uint8)

    bg_resized = cv2.resize(bg_img, (size, size), interpolation=cv2.INTER_CUBIC)

    # 3. Apply Environmental Augmentations

    # Apply color shift (simulates depth/color absorption)
    bg_augmented = apply_color_shift(bg_resized, factor=random.uniform(0.1, 0.3))

    # Apply haze/fog (simulates turbidity/particles)
    bg_augmented = apply_haze_and_fog(bg_augmented, density_range=(0.05, 0.15))

    return bg_augmented





# Step 1: Run your existing augmentation code to fill the data folders:
# generate_augmentations(GREEN_INPUT_IMAGE_PATH, GREEN_OUTPUT_DIR, NUM_AUGMENTATIONS)
# ... (run for RedCrab, JonahCrab)

# Step 2: Collate the paths to all augmented assets
CRAB_ASSET_PATHS = {
    'GreenCrab': [os.path.join('GreenCrabData', f) for f in os.listdir('GreenCrabData') if f.endswith('.jpg')],
    'RockCrab': [os.path.join('RedCrabData', f) for f in os.listdir('RedCrabData') if f.endswith('.jpg')],
    'JonahCrab': [os.path.join('OtherRedCrabData', f) for f in os.listdir('OtherRedCrabData') if f.endswith('.jpg')]
}


# Step 3: Generate the final YOLO dataset
generate_yolo_dataset(CRAB_ASSET_PATHS, 'YOLO_Crab_Detection/data')
print("\nFinal YOLO dataset structure created and labeled!")
