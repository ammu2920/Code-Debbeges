# ML Learning Assistant — Implementation Plan

A multi-modal educational platform for Machine Learning topics, featuring AI-powered Text Explanations, Code Generation, Audio Learning (TTS), and Visual Diagrams. Built with Flask, Google Gemini 2.0 Flash, gTTS, and Vanilla JavaScript.

## Proposed Changes

### Project Root

#### [NEW] requirements.txt
All Python dependencies pinned to the requested versions.

#### [NEW] .env
Template with `GOOGLE_API_KEY` placeholder.

#### [NEW] app.py
Flask application with routes:
- `GET /` → home page
- `POST /api/text` → text explanation via Gemini
- `POST /api/code` → code generation via Gemini
- `POST /api/audio` → TTS via gTTS, returns MP3 URL
- `POST /api/image` → diagram generation via Gemini image model
- `GET /text`, `GET /code`, `GET /audio`, `GET /image` → page routes

---

### Utils

#### [NEW] utils/__init__.py

#### [NEW] utils/genai_utils.py
- Initialises `google-generativeai` client with API key from `.env`
- `get_text_explanation(topic)` — structured prompt, ML-only guard
- `get_code_example(topic, language)` — returns code with explanation
- `is_ml_topic(topic)` — pre-filter using Gemini to confirm topic is AI/ML/DL related; returns 400 if not

#### [NEW] utils/audio_utils.py
- `generate_audio(text, topic)` — gTTS MP3 saved to `static/audio/` with timestamp filename, returns relative URL

#### [NEW] utils/image_utils.py
- `generate_diagram(topic)` — uses Gemini image generation (`gemini-2.0-flash-exp`) to create a diagram; saves to `static/images/` with timestamp filename, returns relative URL

---

### Templates

#### [NEW] templates/base.html
Responsive base with sidebar navigation, Google Fonts (Inter), custom CSS link, and block placeholders (`title`, `content`, `scripts`).

#### [NEW] templates/index.html
Landing page with feature cards for all four modalities.

#### [NEW] templates/text_explanation.html
Form + result area for text explanations; Markdown-rendered output.

#### [NEW] templates/code_generation.html
Form with language selector + Highlight.js code block output.

#### [NEW] templates/audio_learning.html
Form + HTML5 `<audio>` player; shows transcript below.

#### [NEW] templates/image_visualization.html
Form + image gallery output with download option.

---

### Static Files

#### [NEW] static/css/style.css
Dark-mode premium theme:
- CSS variables, glassmorphism cards, gradient hero
- Sidebar nav, responsive grid, micro-animations

#### [NEW] static/js/main.js
Global utilities: toast notifications, loading spinner, theme toggle.

#### [NEW] static/js/text_explanation.js
Fetch `/api/text`, render markdown with `marked.js`.

#### [NEW] static/js/code_generation.js
Fetch `/api/code`, render with Highlight.js, copy-to-clipboard.

#### [NEW] static/js/audio_learning.js
Fetch `/api/audio`, inject `<audio>` player and transcript.

#### [NEW] static/js/image_visualization.js
Fetch `/api/image`, render image gallery with lightbox.

---

## Verification Plan

### Automated / Browser Testing
1. **Start the server**: `cd c:\Users\DELL\OneDrive\Desktop\project && python app.py`
2. Open browser at `http://127.0.0.1:5000`
3. Use the browser subagent to:
   - Visit the home page and verify all 4 feature cards are visible
   - Navigate to Text Explanation, enter "What is a Neural Network?", verify response renders
   - Navigate to Code Generation, enter "Decision Tree in Python", verify syntax-highlighted code appears
   - Navigate to Audio Learning, enter "Explain Gradient Descent", verify audio player appears
   - Navigate to Image Visualization, enter "Convolutional Neural Network", verify image appears
4. Test the ML-only guard: enter "What is the capital of France?" in any form — expect an error toast

### Manual Checks
- Verify `.env` is loaded (API key required from user)
- Verify `static/audio/` and `static/images/` directories are auto-created
- Verify 404 for unknown routes returns gracefully
