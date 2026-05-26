#!/Library/Frameworks/Python.framework/Versions/3.11/bin/python3
import re
import os
import sys

def parse_chord_to_filename(chord_name):
    """Converts a standard chord name to your image file format"""
    match = re.match(r'^([A-G]b?)(.*)$', chord_name)
    if match:
        root, suffix = match.groups()
        return f"{root}-{suffix}.png"
    return f"{chord_name}-.png"

def compile_song(input_filepath):
    if not os.path.exists(input_filepath):
        print(f"Error: {input_filepath} not found.")
        return

    input_dir = os.path.dirname(input_filepath) or "."
    output_file = input_filepath.replace('.txt', '_v7.html')

    with open(input_filepath, 'r') as f:
        lines = f.readlines()

    title = "Song Sheet"
    tuning = "standard"
    unique_chords = set()
    html_lines = []

    for line in lines:
        line = line.rstrip('\n')
        
        if line.startswith('{') and line.endswith('}'):
            meta_match = re.match(r'\{([^:]+):\s*(.+)\}', line)
            if meta_match:
                key, val = meta_match.groups()
                if key.lower() == 'title': title = val.strip()
                if key.lower() == 'tuning': tuning = val.strip().lower()
            continue
            
        if not line.strip():
            html_lines.append('<div class="spacer-line"></div>')
            continue

        clean_line = line.strip(' []\t:')
        if re.match(r'^(Intro|Verse|Chorus|Outro|Bridge|Solo)', clean_line, re.IGNORECASE):
            html_lines.append(f'<div class="section-header">{clean_line.title()}</div>')
            continue

        chords_in_line = re.findall(r'\[([^\]]+)\]', line)
        for c in chords_in_line:
            unique_chords.add(c)

        html_line = re.sub(
            r'\[([^\]]+)\]', 
            r'<span class="chord-label">\1</span>', 
            line
        )
        html_lines.append(f'<div class="lyric-line">{html_line}</div>')

    tuning_folder = "dgbe_chords/baritone_chords" if tuning == "baritone" else "gcea_chords/standard_chords"
    rel_img_dir = os.path.relpath(tuning_folder, input_dir)
    
    print(f"\n--- Building Assets for '{title}' ({tuning} tuning) ---")
    
    sidebar_html = '<div class="chord-grid">\n'
    
    for chord in sorted(unique_chords):
        filename = parse_chord_to_filename(chord)
        img_path = f"{rel_img_dir}/{filename}"
        
        print(f"Mapping '{chord}' -> Linking to: {img_path}")
        
        # Removed the redundant <div class="chord-name"> text
        sidebar_html += f'''
            <div class="chord-box">
                <img src="{img_path}" alt="{chord} chord">
            </div>
        '''
        
    sidebar_html += '</div>\n'
    print("--------------------------------------------------\n")

    # Integrated the new color palette
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{title}</title>
        <style>
            /* Base Page Background */
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background: #4f0a59; color: #e8e8e8; margin: 0; padding: 40px; }}
            .container {{ display: flex; max-width: 1200px; margin: 0 auto; gap: 40px; }}
            
            /* Main Lyrics Area */
            .main-content {{ flex: 1; background: #151133; padding: 40px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); overflow-x: auto; }}
            h1 {{ border-bottom: 2px solid #2a225e; padding-bottom: 10px; color: #ffffff; margin-top: 0; }}
            
            .section-header {{ font-weight: bold; font-size: 1.2em; color: #9c8ae8; margin-top: 25px; margin-bottom: 5px; border-bottom: 1px solid #2a225e; padding-bottom: 5px; }}
            .spacer-line {{ height: 20px; }}

            .song-body {{ font-family: monospace; font-size: 16px; margin-top: 20px; color: #e8e8e8; }}
            .lyric-line {{ line-height: 1.4; margin: 0; white-space: pre-wrap; }}
            .chord-label {{ color: #f39c12; font-weight: bold; font-family: sans-serif; font-size: 15px; }}
            
            /* Sidebar Area */
            .sidebar {{ width: 300px; flex-shrink: 0; position: sticky; top: 40px; height: fit-content; max-height: 90vh; overflow-y: auto; background: #151133; color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }}
            .sidebar h3 {{ margin-top: 0; color: #ffffff; text-align: center; border-bottom: 2px solid #2a225e; padding-bottom: 15px; }}
            
            .chord-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }}
            .chord-box {{ text-align: center; }}
            /* Added white background to images so the black grid lines remain visible against the dark navy */
            .chord-box img {{ max-width: 100%; background: #ffffff; border: 1px solid #2a225e; border-radius: 4px; display: block; margin: 0 auto; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="main-content">
                <h1>{title}</h1>
                <div class="song-body">
                    {''.join(html_lines)}
                </div>
            </div>
            <div class="sidebar">
                <h3>{tuning.capitalize()} Chords</h3>
                {sidebar_html}
            </div>
        </div>
    </body>
    </html>
    """

    with open(output_file, 'w') as f:
        f.write(html_content)
    
    print(f"Success! Compiled {title} into {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: ./compile_v7.py <song_file.txt>")
    else:
        compile_song(sys.argv[1])