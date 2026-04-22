import os

# Path to the RoboFlow labels folder
label_dir = r'C:\Users\User\ROV\X18-CV\Crab_Detection\YOLO_Crab_Detection\improved_data\valid\labels'

def clean_labels(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            file_path = os.path.join(directory, filename)
            
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            new_lines = []
            for line in lines:
                parts = line.split()
                old_cls = int(parts[0])
                
                # --- RELABELING LOGIC ---
                # RoboFlow YAML: 0='0', 1='european crab', 2='european_crab', 3='jonah_crab', 4='rock_crab'
                # Your Model: 0=Green Crab, 1=Rock, 2=Jonah
                
                if old_cls in [1, 2]:   # European Green Crab
                    new_cls = 0
                elif old_cls == 4:      # Rock Crab
                    new_cls = 1
                elif old_cls == 3:      # Jonah Crab
                    new_cls = 2
                else:
                    continue # Skip class '0' if it's junk data
                
                new_lines.append(f"{new_cls} {' '.join(parts[1:])}\n")
            
            # Overwrite with clean data
            with open(file_path, 'w') as f:
                f.writelines(new_lines)

clean_labels(label_dir)
print("RoboFlow labels have been re-indexed to match your model!")