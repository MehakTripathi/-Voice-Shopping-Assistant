# Voice Shopping Assistant - Minimal Demo
This is a simple voice-command shopping list demo using a Flask backend and browser SpeechRecognition API.

## What's included
- `app.py` - Flask backend with simple command parsing and JSON persistence.
- `templates/index.html`, `static/style.css`, `static/script.js`
- `data/shopping_data.json` - persistent store created on first run.

## Run locally
1. Create a virtual environment & install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. Run the app:
   ```bash
   python app.py
   ```
3. Open `http://127.0.0.1:5000` in a Chromium-based browser (Chrome/Edge). Mobile browsers may also work.

## Notes
- This demo uses the browser's speech recognition (no microphone handling on the server).
- It's intentionally lightweight so you can extend NLP, multilingual support, and smart suggestions.
