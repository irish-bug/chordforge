"""
ChordForge v0.2.0
-----------------
Architecture & Backend Updates:
* Split Frontend Routing: Separated the monolithic UI into a dedicated Library Dashboard 
  (/, index.html) and an isolated ChordPro Viewer (/song/<filename>, song.html).
* Multi-Instrument Engine: Added a URL query parameter (?instrument=) to the viewer route, 
  allowing dynamic fetching of instrument-specific chord dictionaries.
* Inline SVG Injection: Replaced legacy raster image logic. The parse_chordpro_to_html 
  function now dynamically injects scaled, lightweight vector graphics (.svg) inline.
* Graceful Fallbacks: Unverified [Chord] tags fall back to a styled, high-visibility 
  text box rather than breaking the UI layout.
* PDF Safety Net: Added extract_text_from_pdf utility. Accidental PDF uploads are 
  quietly parsed to raw text (.txt), preventing server crashes and notifying the user.

Data & Asset Management:
* Vector Migration: Removed Pillow dependency. All diagrams are now scalable XML/SVGs.
* Modular Chord Dictionary: Transitioned from a single master file to a mathematically 
  mapped architecture (chord_data/) supporting 144 chords across 4 distinct tunings 
  (Ukulele, Baritone, 5-String Banjo, and Guitar).
* Automated Centering & Padding: Generator scripts mathematically calculate grid widths 
  based on string count to ensure 4, 5, and 6-string diagrams remain perfectly centered.
"""

import os
import re
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from pypdf import PdfReader

app = Flask(__name__)
app.secret_key = 'chordforge_secret_key'

UPLOAD_FOLDER = 'song_sheets'
STATIC_FOLDER = 'static'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Map folder names to UI display names
INSTRUMENTS = {
    "gcea_chords": "Ukulele (Standard)",
    "dgbe_chords": "Baritone Ukulele",
    "banjo_chords": "5-String Banjo",
    "guitar_chords": "Guitar"
}

def extract_text_from_pdf(pdf_path, output_txt_path):
    """Fallback utility to scrape text from accidental PDF uploads."""
    try:
        reader = PdfReader(pdf_path)
        raw_text = ""
        for page in reader.pages:
            raw_text += page.extract_text() + "\n"
        
        with open(output_txt_path, 'w', encoding='utf-8') as f:
            f.write(raw_text)
        return True
    except Exception as e:
        print(f"Failed to parse PDF: {e}")
        return False

def parse_chordpro_to_html(text, instrument_folder):
    """
    Scans the text for [Chord] tags and replaces them with 
    HTML wrappers pointing to our generated SVG files.
    """
    def chord_replacer(match):
        chord_name = match.group(1).strip()
        # Ensure the filename perfectly matches our new SVG naming convention
        safe_chord = chord_name.replace("_", "")
        svg_path = os.path.join(STATIC_FOLDER, instrument_folder, f"{safe_chord}.svg")
        
        # If we have the SVG, inject it. If not, fallback to a gracefully styled text box.
        if os.path.exists(svg_path):
            img_tag = f'<img src="/{svg_path}" class="chord-diagram" alt="{safe_chord}">'
            return f'<span class="chord-wrapper">{img_tag}<span class="chord-label">{safe_chord}</span></span>'
        else:
            return f'<span class="chord-wrapper missing"><span class="chord-label">[{safe_chord}]</span></span>'

    # Convert the bracketed chords
    parsed_html = re.sub(r'\[(.*?)\]', chord_replacer, text)
    return parsed_html


@app.route('/')
def index():
    # List all available text files
    files = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith('.txt')]
    files.sort()
    return render_template('index.html', songs=files, instruments=INSTRUMENTS)


@app.route('/song/<filename>')
def view_song(filename):
    if not filename.endswith('.txt'):
        abort(404)

    filepath = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(filepath):
        abort(404)

    # Default to standard Uke if no instrument is selected via the query parameter
    active_instrument = request.args.get('instrument', 'gcea_chords')
    if active_instrument not limitations not in INSTRUMENTS:
        active_instrument = 'gcea_chords'

    with open(filepath, 'r', encoding='utf-8') as f:
        raw_content = f.read()

    # Parse the content
    html_content = parse_chordpro_to_html(raw_content, active_instrument)

    return render_template('song.html', 
                           content=html_content, 
                           title=filename.replace('.txt', '').replace('_', ' ').title(),
                           filename=filename,
                           instruments=INSTRUMENTS,
                           active_instrument=active_instrument)


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('index'))

    if file:
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        # The PDF Safety Net
        if file.filename.lower().endswith('.pdf'):
            txt_filename = file.filename.rsplit('.', 1)[0] + '.txt'
            txt_filepath = os.path.join(UPLOAD_FOLDER, txt_filename)
            
            success = extract_text_from_pdf(filepath, txt_filepath)
            os.remove(filepath) # Destroy the PDF immediately
            
            if success:
                flash(f"PDF converted to raw text: {txt_filename}. Please format to ChordPro.")
            else:
                flash("Error: Could not extract text from PDF.")
            
        else:
            flash(f"Successfully uploaded {file.filename}")

        return redirect(url_for('index'))

if __name__ == '__main__':
    # Binding to 0.0.0.0 allows it to be accessed across your local Wi-Fi
    app.run(host='0.0.0.0', port=5000, debug=True)