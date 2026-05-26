from PIL import Image
import os

input_image = "bari-uke-chords_cropped.jpg"
output_dir = "final_chords"  
os.makedirs(output_dir, exist_ok=True)

# YOUR CALIBRATED SETTINGS
start_x = 0  
start_y = 0  
row_height = 71
x_coords = [0, 72, 150, 228, 305, 380, 459, 537, 615, 699, 761] # (Note: You have 11 entries here, using the first 10)
crop_width = 68 

# DEFINE THE MAPPING
# Row 0 = Top, Row 11 = Bottom
# Edit these strings to change how the files are named (e.g., change "Ab" to "A_flat")
row_roots = ["A", "Ab", "B", "Bb", "C", "D", "Db", "E", "Eb", "F", "G", "Gb"]

# These suffixes apply to every row
suffixes = ["", "m", "aug", "dim", "6", "m6", "7", "maj7", "m7", "9"]

img = Image.open(input_image)

for r in range(12):
    for c in range(10):
        # Calculate coordinates based on your calibration
        left = x_coords[c] + start_x
        top = (r * row_height) + start_y
        right = left + crop_width
        bottom = top + row_height
        
        # Crop
        chord_img = img.crop((left, top, right, bottom))
        
        # Build filename: Root + Suffix
        filename = f"{row_roots[r]}{suffixes[c]}.png"
        
        # Save
        chord_img.save(os.path.join(output_dir, filename))
        print(f"Saved: {filename}")

print(f"Success! 120 chords saved to {output_dir}/")