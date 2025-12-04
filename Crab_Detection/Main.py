import cv2
import numpy as np
import os
from PIL import Image

# --- Configuration ---
NUM_AUGMENTATIONS = 1000

# --- Helper Functions for Augmentation ---
def apply_color_shift(image, factor=0.1):
    """Applies a blue/green shift characteristic of underwater environments."""
    img_f = image.astype(np.float32)

    # Increase Blue and Green channels, decrease Red channel (B, G, R)
    b_boost = np.random.uniform(1.0, 1.0 + factor) 
    g_boost = np.random.uniform(1.0, 1.0 + factor)
    r_reduce = np.random.uniform(1.0 - factor, 1.0)
    
    img_f[:, :, 0] *= b_boost # Blue Channel
    img_f[:, :, 1] *= g_boost # Green Channel
    img_f[:, :, 2] *= r_reduce # Red Channel
    
    # Clip values and convert back to 8-bit
    return np.clip(img_f, 0, 255).astype(np.uint8)

def apply_brightness_and_contrast(image):
    """Randomly adjusts brightness and contrast."""
    # Contrast factor (0.5 to 1.5)
    contrast = np.random.uniform(0.7, 1.3)
    # Brightness offset (-30 to 30)
    brightness = np.random.randint(-30, 30)
    
    # The formula is: new_img = alpha * old_img + beta
    # Here, alpha is contrast, beta is brightness
    return cv2.convertScaleAbs(image, alpha=contrast, beta=brightness)

def apply_haze_and_fog(image, density_range=(0.0, 0.2)):
    """Simulates water turbidity by blending with a light color."""
    density = np.random.uniform(*density_range)
    
    # White color (fog) or Light Blue color (haze)
    fog_color = np.array([200, 220, 230], dtype=np.uint8) # BGR: Light blue/white
    
    # Create an overlay layer
    overlay = np.full(image.shape, fog_color, dtype=np.uint8)
    
    # Blend the image and the overlay (density controls blending strength)
    return cv2.addWeighted(image, 1 - density, overlay, density, 0)

def apply_laminate_glare(image):
    """Adds a randomized, localized bright spot to mimic glare/reflection."""
    if np.random.rand() < 0.6: # 60% chance of glare
        h, w, _ = image.shape
        
        # Glare position and size
        center_x = np.random.randint(w // 4, w * 3 // 4)
        center_y = np.random.randint(h // 4, h * 3 // 4)
        radius = np.random.randint(int(min(h, w) * 0.1), int(min(h, w) * 0.3))
        
        # Create a glare mask (a white circle)
        mask = np.zeros((h, w), dtype=np.float32)
        cv2.circle(mask, (center_x, center_y), radius, 255, -1)
        
        # Apply Gaussian blur to make the glare soft
        mask = cv2.GaussianBlur(mask, (0, 0), radius/3)
        
        # Scale the mask to be an opacity layer (0 to 1)
        mask = mask / 255.0
        
        # Combine the glare (white) with the image
        glare_intensity = np.random.uniform(0.3, 0.7)
        
        # Use numpy broadcasting to add glare selectively to BGR channels
        glare_layer = mask[..., np.newaxis] * 255.0 * glare_intensity
        
        final_img = image.astype(np.float32) + glare_layer
        return np.clip(final_img, 0, 255).astype(np.uint8)
    return image

def apply_geometric_transforms(image):
    """Applies small rotation and slight perspective warp."""
    # 1. Rotation (using PIL for easy rotation)
    pil_img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    
    angle = np.random.uniform(-10, 10) # Rotate between -10 and +10 degrees
    rotated_img = pil_img.rotate(angle, resample=Image.Resampling.BILINEAR, expand=False)
    
    # Convert back to OpenCV format
    rotated_img_cv = cv2.cvtColor(np.array(rotated_img), cv2.COLOR_RGB2BGR)

    # 2. Perspective Warp (mimicking water lens effect)
    h, w, _ = rotated_img_cv.shape
    
    # Define source points (corners)
    pts1 = np.float32([[0, 0], [w, 0], [0, h], [w, h]])
    
    # Define destination points (slightly distorted corners)
    # Randomly shift corners by 5-15 pixels
    shift = np.random.randint(5, 15)
    pts2 = np.float32([
        [np.random.randint(-shift, shift), np.random.randint(-shift, shift)],
        [w + np.random.randint(-shift, shift), np.random.randint(-shift, shift)],
        [np.random.randint(-shift, shift), h + np.random.randint(-shift, shift)],
        [w + np.random.randint(-shift, shift), h + np.random.randint(-shift, shift)]
    ])
    
    # Get the transformation matrix and apply it
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    warped_img = cv2.warpPerspective(rotated_img_cv, matrix, (w, h))

    return warped_img

def add_gaussian_noise(image):
    """Adds small amount of noise to simulate film grain or sensor noise."""
    mean = 0
    # Small, random sigma for light noise
    sigma = np.random.uniform(2, 8) 
    
    # Create Gaussian noise
    row, col, ch = image.shape
    gauss = np.random.normal(mean, sigma, (row, col, ch))
    gauss = gauss.reshape(row, col, ch)
    
    # Add noise to the image
    noisy_img = image.astype(np.float32) + gauss
    
    return np.clip(noisy_img, 0, 255).astype(np.uint8)

# --- Main Augmentation Pipeline ---

def generate_augmentations(input_path, output_dir, n_augs):
    """Loads image and generates N augmented versions."""
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    original_img = cv2.imread(input_path)
    if original_img is None:
        print(f"ERROR: Could not load input image from {input_path}. Please check path.")
        return

    print(f"Generating {n_augs} augmentations for {input_path}...")
    
    for i in range(n_augs):
        
        # Start with a copy of the original image
        augmented_img = original_img.copy()

        # 1. Geometric Transforms (Rotation and Warp)
        augmented_img = apply_geometric_transforms(augmented_img)
        
        # 2. Photometric Adjustments (Brightness and Contrast)
        augmented_img = apply_brightness_and_contrast(augmented_img)
        
        # 3. Environmental Effects
        # a. Underwater Color Shift (Blue/Green Hue)
        augmented_img = apply_color_shift(augmented_img, factor=np.random.uniform(0.1, 0.4))
        
        # b. Turbidity/Haze
        augmented_img = apply_haze_and_fog(augmented_img, density_range=(0.05, 0.25))
        
        # c. Laminate Glare/Reflection (Apply last to simulate surface glare)
        augmented_img = apply_laminate_glare(augmented_img)

        # 4. Noise
        augmented_img = add_gaussian_noise(augmented_img)
        
        # Save the augmented image
        output_filename = os.path.join(output_dir, f'aug_{i+1:04d}.jpg')
        cv2.imwrite(output_filename, augmented_img)
        
        if (i + 1) % 100 == 0 or (i + 1) == n_augs:
            print(f" -> Generated {i+1} / {n_augs} images.")

    print(f"\nCompleted. {n_augs} images saved to the '{output_dir}' directory.")


GREEN_INPUT_IMAGE_PATH = 'GreenCrab.jpg' # REPLACE with your actual image path
GREEN_OUTPUT_DIR = 'GreenCrabData'
RED_INPUT_IMAGE_PATH = 'RedCrab.jpg' # REPLACE with your actual image path
RED_OUTPUT_DIR = 'RedCrabData'
OTHER_RED_INPUT_IMAGE_PATH = 'OtherRedCrab.jpg' # REPLACE with your actual image path
OTHER_RED_OUTPUT_DIR = 'OtherRedCrabData'
# --- Execution ---
generate_augmentations(GREEN_INPUT_IMAGE_PATH, GREEN_OUTPUT_DIR, NUM_AUGMENTATIONS)
generate_augmentations(RED_INPUT_IMAGE_PATH, RED_OUTPUT_DIR, NUM_AUGMENTATIONS)
generate_augmentations(OTHER_RED_INPUT_IMAGE_PATH, OTHER_RED_OUTPUT_DIR, NUM_AUGMENTATIONS)