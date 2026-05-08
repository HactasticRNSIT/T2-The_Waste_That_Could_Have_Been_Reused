"""
WasteWise Vision Pipeline — Flask Backend
==========================================
Serves the frontend and proxies the Anthropic Claude Vision API
so the API key is never exposed in the browser.
"""

import os
import json
import base64
import traceback
from datetime import datetime
from io import BytesIO

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests

# ── App setup ────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=BASE_DIR, static_url_path="")
CORS(app)

# In-memory session store (per process; cleared on restart)
session_store: list[dict] = []

# Anthropic key can optionally be set server-side via env var.
# If absent, the client must supply it in the request body.
SERVER_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Serve the main frontend HTML."""
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/api/analyze", methods=["POST"])
def analyze():
    """
    Proxy the Claude Vision API call.

    Expects JSON body:
      {
        "image_b64": "<base64 string, no prefix>",
        "media_type": "image/jpeg" | "image/png" | ...,
        "api_key":    "<optional — overrides server env key>"
      }

    Returns raw Claude JSON response or an error dict.
    """
    body = request.get_json(force=True, silent=True) or {}

    api_key = body.get("api_key", "").strip() or SERVER_API_KEY
    if not api_key:
        return jsonify({"error": "No API key provided. Set ANTHROPIC_API_KEY on the server or pass api_key in the request body."}), 400

    image_b64 = body.get("image_b64", "")
    media_type = body.get("media_type", "image/jpeg")

    if not image_b64:
        return jsonify({"error": "No image data provided (image_b64 is required)."}), 400

    prompt = (
        'Analyze this waste image for a circular-economy dataset. '
        'Respond ONLY with JSON (no markdown):\n'
        '{"item":"specific item name",'
        '"category":"Plastic/Glass/Metal/Paper/Organic/Electronic/Textile/Hazardous/Battery/Medical/Wood/Rubber/Unknown",'
        '"subcategory":"specific type",'
        '"diversion_score":0-100,'
        '"disposal":"best disposal in 6 words",'
        '"recyclable":true/false,'
        '"condition":"good/damaged/contaminated",'
        '"material":"primary material",'
        '"notes":"key visual insight for dataset labeling"}'
    )

    payload = {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 512,
        "messages": [{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": media_type,
                        "data": image_b64
                    }
                },
                {"type": "text", "text": prompt}
            ]
        }]
    }

    try:
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01"
            },
            json=payload,
            timeout=30
        )
        resp.raise_for_status()
        data = resp.json()
        raw_text = data["content"][0]["text"]
        # Strip markdown fences if present
        clean = raw_text.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        ai_result = json.loads(clean)
        return jsonify({"success": True, "result": ai_result})
    except requests.exceptions.HTTPError as e:
        return jsonify({"error": f"Claude API HTTP error: {e.response.status_code}", "detail": e.response.text}), 502
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/session/save", methods=["POST"])
def save_record():
    """
    Persist one analyzed record to the server session store.

    Expects JSON body: any dict (the flattened feature record).
    Adds a server-side timestamp.
    """
    record = request.get_json(force=True, silent=True) or {}
    if not record:
        return jsonify({"error": "Empty record"}), 400
    record["server_saved_at"] = datetime.utcnow().isoformat() + "Z"
    session_store.append(record)
    return jsonify({"success": True, "total": len(session_store)})


@app.route("/api/session/records", methods=["GET"])
def get_records():
    """Return all records saved this session."""
    return jsonify({"records": session_store, "total": len(session_store)})


@app.route("/api/session/clear", methods=["POST"])
def clear_session():
    """Wipe all session records."""
    session_store.clear()
    return jsonify({"success": True})


@app.route("/api/session/export/json", methods=["GET"])
def export_json():
    """Download session records as JSON."""
    from flask import Response
    payload = json.dumps(session_store, indent=2)
    return Response(
        payload,
        mimetype="application/json",
        headers={"Content-Disposition": "attachment; filename=wastewise_session.json"}
    )


@app.route("/api/session/export/csv", methods=["GET"])
def export_csv():
    """Download session records as CSV (flat fields only)."""
    import csv
    from io import StringIO
    from flask import Response

    if not session_store:
        return jsonify({"error": "No records to export"}), 404

    output = StringIO()
    flat_keys = [k for k, v in session_store[0].items() if not isinstance(v, (dict, list))]
    writer = csv.DictWriter(output, fieldnames=flat_keys, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(session_store)
    csv_content = output.getvalue()

    return Response(
        csv_content,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=wastewise_session.csv"}
    )


@app.route("/api/health", methods=["GET"])
def health():
    """Simple health-check endpoint."""
    return jsonify({
        "status": "ok",
        "server_key_set": bool(SERVER_API_KEY),
        "session_records": len(session_store)
    })


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print(" WasteWise Vision Pipeline — Backend Server")
    print(f" Open http://127.0.0.1:5000 in your browser")
    print("=" * 60)
    app.run(debug=True, port=5000)
