"""
app.py — ML Learning Assistant Flask Application
Multi-modal AI educational platform powered by Google Gemini.
"""

import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

from utils.genai_utils import get_text_explanation, get_code_example, get_audio_script, get_image_prompt
from utils.audio_utils import generate_audio, cleanup_old_audio
from utils.image_utils import generate_diagram, cleanup_old_images

# ── App Setup ────────────────────────────────────────────────────────────────

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "ml-learning-assistant-secret")

# Ensure static subdirs exist
os.makedirs(os.path.join("static", "audio"), exist_ok=True)
os.makedirs(os.path.join("static", "images"), exist_ok=True)


# ── Page Routes ──────────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Home / landing page."""
    return render_template("index.html")


@app.route("/text")
def text_page():
    """Text Explanation page."""
    return render_template("text_explanation.html")


@app.route("/code")
def code_page():
    """Code Generation page."""
    return render_template("code_generation.html")


@app.route("/audio")
def audio_page():
    """Audio Learning page."""
    return render_template("audio_learning.html")


@app.route("/image")
def image_page():
    """Image Visualization page."""
    return render_template("image_visualization.html")


# ── API Routes ───────────────────────────────────────────────────────────────

@app.route("/api/text", methods=["POST"])
def api_text():
    """
    POST /api/text
    Body: { "topic": str, "level": str }
    Returns: { "content": str, "topic": str, "level": str } | { "error": str }
    """
    data = request.get_json(silent=True) or {}
    topic = (data.get("topic") or "").strip()
    level = (data.get("level") or "Intermediate").strip()

    if not topic:
        return jsonify({"error": "Topic is required."}), 400

    result = get_text_explanation(topic, level)

    if "error" in result:
        return jsonify(result), 400

    return jsonify(result), 200


@app.route("/api/code", methods=["POST"])
def api_code():
    """
    POST /api/code
    Body: { "topic": str, "language": str, "complexity": str }
    Returns: { "content": str, "topic": str, ... } | { "error": str }
    """
    data = request.get_json(silent=True) or {}
    topic = (data.get("topic") or "").strip()
    language = (data.get("language") or "Python").strip()
    complexity = (data.get("complexity") or "Intermediate").strip()

    if not topic:
        return jsonify({"error": "Topic is required."}), 400

    result = get_code_example(topic, language, complexity)

    if "error" in result:
        return jsonify(result), 400

    return jsonify(result), 200


@app.route("/api/audio", methods=["POST"])
def api_audio():
    """
    POST /api/audio
    Body: { "topic": str, "duration": int, "lang": str }
    Returns: { "audio_url": str, "script": str, ... } | { "error": str }
    """
    data = request.get_json(silent=True) or {}
    topic = (data.get("topic") or "").strip()
    duration = int(data.get("duration") or 3)
    lang = (data.get("lang") or "en").strip()

    if not topic:
        return jsonify({"error": "Topic is required."}), 400

    # Generate script via Gemini
    script_result = get_audio_script(topic, duration)
    if "error" in script_result:
        return jsonify(script_result), 400

    script = script_result["script"]

    # Convert to audio
    cleanup_old_audio(max_files=50)
    audio_result = generate_audio(script, topic, lang=lang)
    if "error" in audio_result:
        return jsonify(audio_result), 500

    return jsonify({
        **audio_result,
        "script": script,
        "topic": topic,
    }), 200


@app.route("/api/image", methods=["POST"])
def api_image():
    """
    POST /api/image
    Body: { "topic": str, "diagram_type": str }
    Returns: { "image_url": str, ... } | { "error": str, "fallback_description": str }
    """
    data = request.get_json(silent=True) or {}
    topic = (data.get("topic") or "").strip()
    diagram_type = (data.get("diagram_type") or "Architecture Diagram").strip()

    if not topic:
        return jsonify({"error": "Topic is required."}), 400

    # Generate image prompt via Gemini text model
    prompt_result = get_image_prompt(topic, diagram_type)
    if "error" in prompt_result:
        return jsonify(prompt_result), 400

    # Generate actual diagram image
    cleanup_old_images(max_files=30)
    image_result = generate_diagram(topic, prompt_result["prompt"], diagram_type)

    if "error" in image_result and "fallback_description" not in image_result:
        return jsonify(image_result), 500

    return jsonify({
        **image_result,
        "image_prompt": prompt_result["prompt"],
    }), 200


# ── Error Handlers ────────────────────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    return render_template("index.html"), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error. Please try again."}), 500


# ── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1", "yes")
    app.run(debug=debug, host="0.0.0.0", port=5000)
