# ChordForge 🎸

**Version:** 0.2.0

ChordForge is a lightweight, Flask-based local web application designed to parse standard ChordPro text files and instantly inject mathematically accurate, instrument-specific SVG chord diagrams directly above the lyrics. 

Built to run seamlessly on a local network (like a Raspberry Pi) and scale beautifully on mobile screens.

## 🚀 Features

* **Multi-Instrument Engine:** Dynamically swap between standard Ukulele, Baritone Ukulele, 5-String Banjo, and Guitar voicings without altering the source text file.
* **Vector Graphics:** Automatically generates and serves mathematically scaled, crisp `.svg` diagrams. No blurry rasters, no pixelation on large screens.
* **Smart Parsing:** Wrap chords in brackets [Cm7] in your text file, and ChordForge maps them to the corresponding diagram on the fly.
* **Graceful Fallbacks:** If an obscure chord isn't in the generated library yet, the app falls back to a highly visible text block so you never lose your place in the song.
* **PDF Safety Net:** Accidentally uploaded a PDF? The backend quietly rips the raw text into a safe `.txt` file for you to format, preventing server crashes.
* **Modular Library:** The chord_data/ architecture uses standard CAGED logic to map 144 movable chord shapes across multiple tunings.

## 🛠️ Installation

1. Clone the repository
2. Set up a virtual environment (e.g., `python3 -m venv chords_env` then activate it)
3. Install dependencies via `pip install Flask pypdf` (Note: The heavy Pillow dependency was removed in v0.2.0!)

## 🎵 Usage

1. Start the server using `python app.py`
2. Open a web browser on any device on your Wi-Fi network and navigate to your host's IP address (e.g., http://192.168.1.XX:5000)
3. Upload a standard `.txt` file containing your lyrics and bracketed chords. Click the song in the library to open the viewer.

## 📁 Project Structure

ChordForge/
├── app.py                  # Main Flask backend and routing
├── generate_chords.py      # Master SVG generation script
├── chord_data/             # Modular Python files storing array data (c.py, d.py...)
├── static/                 # Generated SVG files sorted by instrument
│   ├── gcea_chords/        
│   ├── dgbe_chords/        
│   ├── banjo_chords/       
│   └── guitar_chords/      
├── templates/              
│   ├── index.html          # Dashboard and Library view
│   └── song.html           # Dedicated ChordPro rendering view
└── song_sheets/            # Uploaded .txt files live here

## 📝 Changelog (v0.2.0)
* Split Frontend Routing: Separated the monolithic UI into a dedicated Library Dashboard and an isolated ChordPro Viewer.
* Multi-Instrument Engine: Added URL query parameters to dynamically fetch instrument-specific chord dictionaries via a UI dropdown.
* Inline SVG Injection: Replaced legacy raster image logic. Chords are now lightweight `.svg` vector graphics.
* Modular Chord Dictionary: Transitioned from a single master file to a mathematically mapped architecture supporting 144 chords across 4 distinct tunings.
* Automated Centering: Generator scripts now mathematically calculate grid widths based on string count to ensure perfect visual alignment.