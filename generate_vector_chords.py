import os
import shutil

# Import the 12 data modules
from chord_data.c import C_CHORDS
from chord_data.db import DB_CHORDS
from chord_data.d import D_CHORDS
from chord_data.eb import EB_CHORDS
from chord_data.e import E_CHORDS
from chord_data.f import F_CHORDS
from chord_data.gb import GB_CHORDS
from chord_data.g import G_CHORDS
from chord_data.ab import AB_CHORDS
from chord_data.a import A_CHORDS
from chord_data.bb import BB_CHORDS
from chord_data.b import B_CHORDS

INSTRUMENTS = {
    "gcea_chords": 4,
    "dgbe_chords": 4,
    "banjo_chords": 5,
    "guitar_chords": 6
}

# Python unpacks (**) and merges all 12 dictionaries into one master library instantly
CHORD_LIBRARY = {
    **C_CHORDS, **DB_CHORDS, **D_CHORDS, **EB_CHORDS, 
    **E_CHORDS, **F_CHORDS, **GB_CHORDS, **G_CHORDS, 
    **AB_CHORDS, **A_CHORDS, **BB_CHORDS, **B_CHORDS
}

def draw_chord_svg(fret_array, chord_name, num_strings):
    string_spacing = 30
    board_width = (num_strings - 1) * string_spacing
    width = board_width + 100 
    height = 200
    grid_start_x = (width - board_width) / 2
    
    svg = [f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">']
    
    # Centered Bold Title
    svg.append(f'<text x="{width/2}" y="50" font-family="sans-serif" font-size="24" font-weight="bold" text-anchor="middle">{chord_name}</text>')
    
    active_frets = [f for f in fret_array if f > 0]
    min_fret = min(active_frets, default=1)
    offset = min_fret - 1 if min_fret > 1 else 0
    
    if offset > 0:
        svg.append(f'<text x="{grid_start_x - 35}" y="90" font-family="sans-serif" font-size="16" font-weight="bold" text-anchor="start">{min_fret}fr</text>')

    for i in range(5):
        y = 70 + (i * 30)
        svg.append(f'<line x1="{grid_start_x}" y1="{y}" x2="{grid_start_x + board_width}" y2="{y}" stroke="black" stroke-width="2"/>')
    
    for i in range(num_strings):
        x = grid_start_x + (i * string_spacing)
        svg.append(f'<line x1="{x}" y1="70" x2="{x}" y2="190" stroke="black" stroke-width="2"/>')
        
        fret = fret_array[i]
        if fret == -1:
            # TWEAKED HERE: Dropped font-size to 14, moved down to y=65
            svg.append(f'<text x="{x}" y="65" font-family="sans-serif" font-size="14" text-anchor="middle">x</text>')
        elif fret > 0:
            y = 70 + ((fret - offset - 1) * 30) + 15
            svg.append(f'<circle cx="{x}" cy="{y}" r="9" fill="black"/>')
            
    svg.append('</svg>')
    return "\n".join(svg)

def generate_all():
    for tuning_folder, num_strings in INSTRUMENTS.items():
        static_path = f"static/{tuning_folder}"
        if os.path.exists(static_path):
            shutil.rmtree(static_path)
        os.makedirs(static_path, exist_ok=True)
        
        for name, instrument_map in CHORD_LIBRARY.items():
            frets = instrument_map.get(tuning_folder)
            if not frets or len(frets) != num_strings:
                continue
            with open(f"{static_path}/{name}.svg", "w") as f:
                f.write(draw_chord_svg(frets, name, num_strings))
            # print(f"Generated: {name}.svg for {tuning_folder}") # Commented out so it doesn't spam your terminal with 576 lines

    print("All SVGs successfully generated and sorted!")

if __name__ == "__main__":
    generate_all()