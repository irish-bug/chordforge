#!/home/shane/Documents/ukulele_chords/chords_conversion_env/bin/python
# Version 1.9
# Changelog:
# - Added TEMPLATES_AUTO_RELOAD so index.html and chart.html update without restarting Flask.
# - Added 'Artist' to the ChordPro metadata parser.
# - Passed 'artist' variable to the view_song template renderer.

import os
import re
from flask import Flask, render_template, request, redirect, url_for
from pypdf import PdfReader

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'song_sheets'
app.config['TEMPLATES_AUTO_RELOAD'] = True # This forces Flask to watch your HTML files!

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static/dgbe_chords', exist_ok=True)
os.makedirs('static/gcea_chords', exist_ok=True)
os.makedirs('static/banjo_chords', exist_ok=True)
os.makedirs('static/guitar_chords', exist_ok=True)

def parse_chord_to_filename(chord_name):
    root_chord = chord_name.split('/')[0].strip()
    enharmonic_map = {'C#': 'Db', 'D#': 'Eb', 'F#': 'Gb', 'G#': 'Ab', 'A#': 'Bb'}
    match = re.match(r'^([A-G][b#]?)(.*)$', root_chord)
    
    if match:
        root, suffix = match.groups()
        root = root.strip()
        if root in enharmonic_map:
            root = enharmonic_map[root]
        safe_suffix = suffix.strip().replace('#', 's')
        return f"{root}{safe_suffix}.svg"
        
    safe_name = root_chord.replace('#', 's')
    return f"{safe_name}.svg"

def is_chord_line(line):
    cleaned = line.strip()
    if not cleaned: return False
    cleaned = re.sub(r'\(.*?\)', '', cleaned).strip()
    tokens = cleaned.split()
    if not tokens: return False
    chord_pattern = re.compile(r'^[A-G][b#]?(m|min|maj|M|dim|aug|sus)?\d*(/[A-G][b#]?)?$', re.IGNORECASE)
    for token in tokens:
        if not chord_pattern.match(token):
            return False 
    return True

def convert_to_chordpro(text):
    lines = text.splitlines()
    out_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if "Page " in line and "/" in line:
            i += 1
            continue
        # Updated Regex to catch 'Artist'
        meta_match = re.match(r'^(Tuning|Key|Capo|Difficulty|Strum|Artist):\s*(.+)', line, re.IGNORECASE)
        if meta_match:
            key, val = meta_match.groups()
            out_lines.append(f"{{{key}: {val}}}")
            i += 1
            continue
        if is_chord_line(line):
            if i + 1 < len(lines) and lines[i+1].strip() and not is_chord_line(lines[i+1]) and not lines[i+1].startswith('['):
                chord_line = line
                lyric_line = lines[i+1]
                chords = [(match.start(), match.group()) for match in re.finditer(r'\S+', chord_line)]
                lyric_chars = list(lyric_line)
                for pos, chord in reversed(chords):
                    chord_str = f"[{chord}]"
                    if pos >= len(lyric_chars):
                        lyric_chars.extend([' '] * (pos - len(lyric_chars)))
                        lyric_chars.append(chord_str)
                    else:
                        lyric_chars.insert(pos, chord_str)
                out_lines.append("".join(lyric_chars))
                i += 2 
                continue
            else:
                spaced_chords = re.sub(r'(\S+)', r'[\1]', line)
                out_lines.append(spaced_chords)
                i += 1
                continue
        out_lines.append(line)
        i += 1
    return "\n".join(out_lines)

@app.route('/')
def index():
    songs = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if f.endswith('.txt')]
    songs.sort()
    return render_template('index.html', songs=songs, current_song=None)

@app.route('/chart/<instrument>')
def view_chart(instrument):
    mapping = {
        'gcea': 'gcea_chords', 
        'dgbe': 'dgbe_chords', 
        'banjo': 'banjo_chords', 
        'guitar': 'guitar_chords'
    }
    tuning_names = {
        'gcea': 'GCEA Ukulele', 
        'dgbe': 'DGBE Ukulele', 
        'banjo': 'Banjo', 
        'guitar': 'Guitar'
    }
    folder = mapping.get(instrument, 'gcea_chords')
    tuning_display = tuning_names.get(instrument, 'GCEA Ukulele')
    path = os.path.join('static', folder)
    
    chord_files = [f for f in os.listdir(path) if f.endswith('.svg')]
    chord_files.sort()

    grouped_chords = {}
    for chord in chord_files:
        root_letter = chord[0].upper()
        if root_letter not in grouped_chords:
            grouped_chords[root_letter] = []
        grouped_chords[root_letter].append(chord)
        
    grouped_chords = {k: grouped_chords[k] for k in sorted(grouped_chords)}
    
    return render_template('chart.html', instrument=instrument, tuning_display=tuning_display, grouped_chords=grouped_chords, folder=folder)

@app.route('/song/<filename>')
def view_song(filename):
    tuning_pref = request.args.get('tuning', 'gcea')
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    if not os.path.exists(filepath):
        return redirect(url_for('index'))

    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    title = filename.replace('.txt', '').replace('_', ' ').title()
    strum_pattern = None
    artist = None
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
                elif key.lower() == 'strum': strum_pattern = val.strip()
                elif key.lower() == 'artist': artist = val.strip() # Extracted artist tag
            continue
            
        if not line.strip():
            html_lines.append('<div class="spacer-line"></div>')
            continue

        clean_line = line.strip(' []\t:')
        if re.match(r'^(Intro|Verse|Chorus|Post-Chorus|Interlude|Outro|Bridge|Solo|Instrumental|Pre[\s\-]?Chorus|Break)', clean_line, re.IGNORECASE):
            html_lines.append(f'<div class="section-header">{clean_line.title()}</div>')
            continue

        chords_in_line = re.findall(r'\[([^\]]+)\]', line)
        for c in chords_in_line:
            clean_c = c.strip()
            if clean_c: unique_chords.add(clean_c)

        if re.match(r'^(\s*\[[^\]]+\]\s*)+$', line):
            html_line = re.sub(r'\[([^\]]+)\]', r'<span class="chord-label-standalone">\1</span>', line)
            html_lines.append(f'<div class="lyric-line chord-only-line">{html_line}</div>')
        else:
            html_line = re.sub(r'\[([^\]]+)\]', r'<span class="chord-label-inline" data-chord="\1"></span>', line)
            html_lines.append(f'<div class="lyric-line">{html_line}</div>')

    if tuning == 'dgbe': tuning_folder = "dgbe_chords"
    elif tuning == 'banjo': tuning_folder = "banjo_chords"
    elif tuning == 'guitar': tuning_folder = "guitar_chords"
    else: tuning_folder = "gcea_chords"

    tuning_names = {
        'gcea': 'GCEA Ukulele', 
        'dgbe': 'DGBE Ukulele', 
        'banjo': 'Banjo', 
        'guitar': 'Guitar'
    }
    tuning_display = tuning_names.get(tuning, 'GCEA Ukulele')
        
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
                           artist=artist,
                           strum_pattern=strum_pattern,
                           html_lines=html_lines, 
                           chord_data=chord_data,
                           tuning=tuning,
                           tuning_display=tuning_display)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    
    raw_text = ""
    if file.filename.endswith('.txt'):
        raw_text = file.read().decode('utf-8', errors='ignore')
    elif file.filename.endswith('.pdf'):
        try:
            reader = PdfReader(file)
            raw_text = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
        except Exception as e:
            print(f"Failed to read PDF: {e}")
            return redirect(request.url)
    else:
        return redirect(request.url)

    chordpro_text = convert_to_chordpro(raw_text)
    safe_name = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', file.filename.rsplit('.', 1)[0]) + '.txt'
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], safe_name)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(chordpro_text)
        
    return redirect(url_for('view_song', filename=safe_name))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)