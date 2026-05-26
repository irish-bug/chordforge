from PIL import Image
import os

input_image = "bari-uke-chords_cropped.jpg"
output_dir = "debug_crop"
os.makedirs(output_dir, exist_ok=True)

# Set these to 0,0 to see exactly where the crop starts
# Then adjust them by nudging until the "A" chord is centered
start_x = 0  
start_y = 0  
row_height = 71
x_coords = [0, 72, 150, 228, 305, 380, 459, 537, 615, 699, 761]
crop_width = 68 

img = Image.open(input_image)

# Only loop through the first 2 rows and columns to debug
for r in range(12):
    for c in range(10):
        left = x_coords[c] + start_x
        top = (r * row_height) + start_y
        right = left + crop_width
        bottom = top + row_height
        
        chord_img = img.crop((left, top, right, bottom))
        chord_img.save(f"{output_dir}/debug_row{r}_col{c}.png")

print("Check the 'debug_crop' folder.")