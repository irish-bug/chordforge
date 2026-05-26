#Update 0.0.3
#add a new function called convert_to_chordpro to allow upload of tab site style text and pdfs. 

#!/home/shane/Documents/ukulele_chords/chords_conversion_env/bin/python
import os
import re
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'song_sheets'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static/dgbe_chords', exist_ok=True)
os.makedirs('static/gcea_chords', exist_ok=True)
os.makedirs('static/banjo_chords', exist_ok=True)

def parse_chord_to_filename(chord_name):
    chord_name = chord_name.strip()
    enharmonic_map = {'C#': 'Db', 'D#': 'Eb', 'F#': 'Gb', 'G#': 'Ab', 'A#': 'Bb'}
    match = re.match(r'^([A-G][b#]?)(.*)$', chord_name)
    if match:
        root, suffix = match.groups()
        root = root.strip()
        if root in enharmonic_map:
            root = enharmonic_map[root]
        return f"{root}-{suffix.strip()}.png"
    return f"{chord_name}-.png"

def is_chord_line(line):
    """Detects if a line consists entirely of guitar/ukulele chords."""
    cleaned = line.strip()
    if not cleaned: return False
    
    # Strip common non-chord artifacts like (play loud) or (x3)
    cleaned = re.sub(r'\(.*?\)', '', cleaned).strip()
    tokens = cleaned.split()
    if not tokens: return False

    # Standard music theory regex for chords
    chord_pattern = re.compile(r'^[A-G][b#]?(m|min|maj|M|dim|aug|sus)?\d*(/[A-G][b#]?)?$', re.IGNORECASE)
    
    for token in tokens:
        if not chord_pattern.match(token):
            return False # If any word isn't a chord, it's probably lyrics
    return True

def convert_to_chordpro(text):
    """Auto-converts standard tabs into inline ChordPro format."""
    lines = text.splitlines()
    out_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]
        
        # Clean up page numbers and junk from PDF rips
        if "Page " in line and "/" in line:
            i += 1
            continue

        # Catch Meta Tags
        meta_match = re.match(r'^(Tuning|Key|Capo|Difficulty):\s*(.+)', line, re.IGNORECASE)
        if meta_match:
            key, val = meta_match.groups()
            out_lines.append(f"{{{key}: {val}}}")
            i += 1
            continue

        # Check if current line is a chord line
        if is_chord_line(line):
            # Check if the next line is lyrics
            if i + 1 < len(lines) and lines[i+1].strip() and not is_chord_line(lines[i+1]) and not lines[i+1].startswith('['):
                chord_line = line
                lyric_line = lines[i+1]

                # Find the exact character index of each chord
                chords = [(match.start(), match.group()) for match in re.finditer(r'\S+', chord_line)]
                lyric_chars = list(lyric_line)

                # Insert from right-to-left so we don't shift the string indices
                for pos, chord in reversed(chords):
                    chord_str = f"[{chord}]"
                    if pos >= len(lyric_chars):
                        # If the chord floats past the end of the lyric line, pad with spaces
                        lyric_chars.extend([' '] * (pos - len(lyric_chars)))
                        lyric_chars.append(chord_str)
                    else:
                        lyric_chars.insert(pos, chord_str)

                out_lines.append("".join(lyric_chars))
                i += 2 # Skip the lyric line since we just merged it
                continue
            else:
                # If it's a chord line but no lyrics follow (like an Intro), just bracket them
                chords = [f"[{match.group()}]" for match in re.finditer(r'\S+', line)]
                out_lines.append(" ".join(chords))
                i += 1
                continue

        # Normal line pass-through
        out_lines.append(line)
        i += 1

    return "\n".join(out_lines)

@app.route('/')
def index():
    songs = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if f.endswith('.txt')]
    songs.sort()
    return render_template('index.html', songs=songs, current_song=None)

@app.route('/song/<filename>')
def view_song(filename):
    tuning_pref = request.args.get('tuning', 'standard')
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    if not os.path.exists(filepath):
        return redirect(url_for('index'))

    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    title = filename.replace('.txt', '').replace('_', ' ').title()
    tuning = tuning_pref
    unique_chords = set()
    html_lines = []

    for line in lines:
        line = line.replace('\r', '').rstrip('\n')
        
        if line.startswith('{') and line.endswith('}'):
            meta_match = re.match(r'\{([^:]+):\s*(.+)\}', line)
            if meta_match:
                key, val = meta_match.groups()
                if key.lower() == 'title': title = val.strip()
            continue
            
        if not line.strip():
            html_lines.append('<div class="spacer-line"></div>')
            continue

        clean_line = line.strip(' []\t:')
        if re.match(r'^(Intro|Verse|Chorus|Outro|Bridge|Solo|Instrumental|Pre[\s\-]?Chorus|Break)', clean_line, re.IGNORECASE):
            html_lines.append(f'<div class="section-header">{clean_line.title()}</div>')
            continue

        chords_in_line = re.findall(r'\[([^\]]+)\]', line)
        for c in chords_in_line:
            clean_c = c.strip()
            if clean_c: 
                unique_chords.add(clean_c)

        html_line = re.sub(r'\[([^\]]+)\]', r'<span class="chord-label">\1</span>', line)
        html_lines.append(f'<div class="lyric-line">{html_line}</div>')

    if tuning == 'baritone':
        tuning_folder = "dgbe_chords"
    elif tuning == 'banjo':
        tuning_folder = "banjo_chords"
    else:
        tuning_folder = "gcea_chords"
        
    chord_data = []
    for chord in sorted(unique_chords):
        img_name = parse_chord_to_filename(chord)
        img_path = url_for('static', filename=f"{tuning_folder}/{img_name}")
        chord_data.append({'name': chord, 'path': img_path})

    songs = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if f.endswith('.txt')]
    songs.sort()

    return render_template('index.html', 
                           songs=songs, 
                           current_song=filename,
                           title=title, 
                           html_lines=html_lines, 
                           chord_data=chord_data,
                           tuning=tuning)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    
    if file and file.filename.endswith('.txt'):
        raw_text = file.read().decode('utf-8', errors='ignore')
        
        # Intercept the raw text and force it into ChordPro!
        chordpro_text = convert_to_chordpro(raw_text)
        
        safe_name = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], safe_name)
        
        # Save the fully converted file to the hard drive
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(chordpro_text)
            
        return redirect(url_for('view_song', filename=safe_name))
        
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)