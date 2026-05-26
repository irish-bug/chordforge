
```markdown
# ChordForge 🎸

A lightweight, self-hosted web application for string musicians. 

ChordForge is a dynamic song library and chord visualizer designed to run on a local network (like a Raspberry Pi 5). It allows you to upload raw text tabs from the internet and instantly view them in a clean, dark-mode interface with mathematically generated chord diagrams. 

It is designed to be accessible from any device on your Wi-Fi, making it the perfect companion to pull up on a phone or tablet while you are holding your instrument.

## ✨ Features

* **Intelligent Auto-Converter:** Drop in messy text files, Ultimate Guitar tabs, or raw PDF extractions. The backend engine automatically scrubs the text, detects chord lines, and perfectly interleaves them into an inline ChordPro-style format.
* **Dynamic Image Generation:** No more hunting for low-res JPEG chord charts. The app uses Python (Pillow) to draw mathematically perfect, transparent PNG chord grids on the fly. 
* **Multi-Instrument Support:** Instantly toggle the active tuning of any song. The app currently supports:
    * Standard Ukulele (gCEA)
    * Baritone Ukulele (DGBE)
    * Banjo (Custom 4-string)
* **Graceful Fallbacks:** If a song contains an obscure chord that isn't in your local dictionary, the UI elegantly handles it with a placeholder box rather than breaking the layout.
* **Native Dark Mode:** A high-contrast, deep purple/navy UI designed to be easy on the eyes in a studio environment.

## 🚀 Installation & Deployment

This application is built with Python and Flask. You can run it directly in a virtual environment or deploy it as a Docker container.

### Option 1: Local Python Environment
1. Clone this repository:
```bash
git clone [https://github.com/yourusername/chordforge.git](https://github.com/yourusername/chordforge.git)
cd chordforge
```
2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```
3. Install the dependencies:
```bash
pip install Flask Pillow
```
4. Generate the initial chord libraries:
```bash
python app/generate_chords.py
```
5. Start the server:
```bash
python app.py
```

### Option 2: Docker (Recommended for Raspberry Pi / Always-On Servers)
You can containerize the entire application so it runs silently in the background on your network.
1. Build the image:
```bash
docker build -t chordforge .
```
2. Run the container on port 5000:
```bash
docker run -d -p 5000:5000 --name chord-server chordforge
```

## 🛠 Adding Custom Chords
ChordForge does not rely on third-party APIs. You have complete control over the voicings. 
To add a new chord to the library:
1. Open `generate_chords.py`.
2. Add your desired fingering to the dictionary using a fret array (e.g., `"Fsus2": [0, 0, 1, 3]`). `0` is an open string, `-1` or `x` is a muted string.
3. Run the generator script again. The new transparent PNG will be instantly stamped out and available to the web server. 

## 📁 Project Structure

```text
├── app.py                  # Main Flask web server and parsing engine
├── generate_chords.py      # Python script to draw perfectly uniform chord PNGs
├── Dockerfile              # Deployment instructions
├── templates/
│   └── index.html          # Main UI layout 
├── static/                 # Generated chord images live here
│   ├── gcea_chords/
│   ├── dgbe_chords/
│   └── banjo_chords/
└── song_sheets/            # Uploaded text and ChordPro files
```

```
