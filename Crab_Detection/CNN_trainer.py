import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
import numpy as np
import os
from PIL import Image

# --- 1. Configuration and Setup ---

# Define data directories.
# NOTE: Replace these with the actual paths once you have organized your augmented data.
# For this script to run, you need three folders inside a 'data' directory.
# UPDATED: Assuming three distinct pipe conditions for multi-class classification:
CLASS_NAMES = ['GreenCrabData', 'RedCrabData', 'OtherRedCrabData'] 
BATCH_SIZE = 32
NUM_EPOCHS = 10
LEARNING_RATE = 0.001

# Ensure device is set to GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")
exit(0)
# --- 2. Custom Dataset Class (To load and transform data) ---

class PipeDataset(Dataset):
    """A custom dataset class to load images from directories."""
    def __init__(self, root_dir, class_names, transform=None):
        self.root_dir = root_dir
        self.transform = transform
        self.class_names = class_names
        self.image_paths = []
        self.labels = []
        
        # Populate image paths and labels
        for i, class_name in enumerate(self.class_names):
            class_path = os.path.join(self.root_dir, class_name)
            if not os.path.exists(class_path):
                print(f"Warning: Directory {class_path} not found. Skipping class.")
                continue
                
            for filename in os.listdir(class_path):
                if filename.endswith(('.png', '.jpg', '.jpeg')):
                    self.image_paths.append(os.path.join(class_path, filename))
                    self.labels.append(i) # Assign label index

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        # Load image using PIL
        img_path = self.image_paths[idx]
        image = Image.open(img_path).convert('RGB')
        
        # Get label
        label = self.labels[idx]
        
        # Apply transformations
        if self.transform:
            image = self.transform(image)
        
        return image, label

# --- 3. Image Preprocessing and Augmentation ---

# Note: The 'augment_image.py' script handles the complex offline augmentation.
# These transformations handle standard PyTorch preprocessing (normalization, tensor conversion).

image_size = (128, 128) # Resize images to a standard size for the CNN

# Transformations applied during training
train_transform = transforms.Compose([
    transforms.Resize(image_size), 
    # Use standard geometric augmentations provided by torchvision (in addition to your custom ones)
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(5),
    transforms.ToTensor(), # Converts PIL Image to PyTorch Tensor
    # Normalization using standard ImageNet mean/std (or calculate your own dataset mean/std)
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]) 
])

# Transformations applied during validation/testing
val_transform = transforms.Compose([
    transforms.Resize(image_size),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])


# --- 4. Model Definition (Simple CNN Architecture) ---
# [Image of Convolutional Neural Network Architecture]

class SimpleCNN(nn.Module):
    """A simple 4-layer Convolutional Neural Network."""
    def __init__(self, num_classes):
        super(SimpleCNN, self).__init__()
        
        # 1. Convolutional Block 1
        self.layer1 = nn.Sequential(
            nn.Conv2d(3, 16, kernel_size=5, stride=1, padding=2), # Input: 3x128x128, Output: 16x128x128
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2)                 # Output: 16x64x64
        )
        
        # 2. Convolutional Block 2
        self.layer2 = nn.Sequential(
            nn.Conv2d(16, 32, kernel_size=5, stride=1, padding=2), # Output: 32x64x64
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2)                 # Output: 32x32x32
        )
        
        # 3. Convolutional Block 3
        self.layer3 = nn.Sequential(
            nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1), # Output: 64x32x32
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2)                 # Output: 64x16x16
        )

        # 4. Fully Connected Layer
        # The input size (64 * 16 * 16) is calculated based on the output of the last max pooling layer
        self.fc = nn.Linear(64 * 16 * 16, num_classes) 

    def forward(self, x):
        out = self.layer1(x)
        out = self.layer2(out)
        out = self.layer3(out)
        
        # Flatten the output for the fully connected layer
        out = out.reshape(out.size(0), -1) 
        out = self.fc(out)
        return out

# --- 5. Training Loop Function ---

def train_model(model, train_loader, val_loader):
    """Main function to train and validate the model."""
    
    # Loss and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
    
    model.train() # Set the model to training mode
    
    for epoch in range(NUM_EPOCHS):
        running_loss = 0.0
        
        # Training Phase
        for i, (images, labels) in enumerate(train_loader):
            images = images.to(device)
            labels = labels.to(device)
            
            # Forward pass
            outputs = model(images)
            loss = criterion(outputs, labels)
            
            # Backward and optimize
            optimizer.zero_grad() # Clear previous gradients
            loss.backward()       # Compute gradient
            optimizer.step()      # Update weights
            
            running_loss += loss.item() * images.size(0)
            
            if (i + 1) % 50 == 0:
                print (f'Epoch [{epoch+1}/{NUM_EPOCHS}], Step [{i+1}/{len(train_loader)}], Loss: {loss.item():.4f}')

        epoch_loss = running_loss / len(train_loader.dataset)
        print(f'Epoch {epoch+1} finished. Training Loss: {epoch_loss:.4f}')

        # Validation Phase
        validate_model(model, val_loader)

# --- 6. Evaluation Function ---

def validate_model(model, val_loader):
    """Evaluates the model on the validation set."""
    model.eval() # Set the model to evaluation mode
    correct = 0
    total = 0
    
    with torch.no_grad(): # Disable gradient calculation during validation
        for images, labels in val_loader:
            images = images.to(device)
            labels = labels.to(device)
            
            outputs = model(images)
            _, predicted = torch.max(outputs.data, 1) # Get the predicted class
            
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

    accuracy = 100 * correct / total
    print(f'Validation Accuracy: {accuracy:.2f}%')
    model.train() # Switch back to training mode


# --- 7. Main Execution ---

if __name__ == '__main__':
    
    # 7.1. Create mock data structure if necessary
    # Since this environment cannot execute file system operations directly, 
    # the user MUST ensure 'data/normal_pipe', 'data/minor_defect', and 'data/major_defect' exist 
    # and are populated with images (e.g., from running augment_image.py).
    
    print("\n--- Initializing Data Loaders ---")
    
    # In a real scenario, you'd split the dataset before creating the loaders.
    # We will instantiate the full dataset twice with different transforms here for simplicity.
    try:
        full_dataset = PipeDataset(DATA_ROOT, CLASS_NAMES, transform=None)
        
        # Split the dataset into 80% training and 20% validation
        train_size = int(0.8 * len(full_dataset))
        val_size = len(full_dataset) - train_size
        
        # Check if dataset is empty
        if len(full_dataset) == 0:
            # Updated error message to reflect 3 directories
            print(f"FATAL ERROR: Dataset is empty. Please ensure data directory structure is correct: {DATA_ROOT}/(normal_pipe, minor_defect, major_defect) and contains images.")
        else:
            # Use random_split to get indices for train/val split
            train_dataset, val_dataset = torch.utils.data.random_split(full_dataset, [train_size, val_size])

            # Apply specific transforms to the partitioned datasets
            train_dataset.dataset.transform = train_transform
            val_dataset.dataset.transform = val_transform

            # Create data loaders
            train_loader = DataLoader(dataset=train_dataset, batch_size=BATCH_SIZE, shuffle=True)
            val_loader = DataLoader(dataset=val_dataset, batch_size=BATCH_SIZE, shuffle=False)
            
            print(f"Train samples: {len(train_dataset)}, Validation samples: {len(val_dataset)}")
            
            # 7.2. Initialize Model
            # This line automatically picks up the number of classes (3)
            num_classes = len(CLASS_NAMES)
            model = SimpleCNN(num_classes).to(device)
            
            # 7.3. Start Training
            print("\n--- Starting Training ---")
            train_model(model, train_loader, val_loader)

            # 7.4. Save the final model
            model_save_path = 'pipe_cnn_model.pth'
            torch.save(model.state_dict(), model_save_path)
            print(f"\nModel training finished and saved to {model_save_path}")

    except Exception as e:
        print(f"\nAn error occurred during PyTorch execution. Check your data path and file structure.")
        print(f"Detail: {e}")