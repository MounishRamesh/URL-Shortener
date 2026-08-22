import os
import sqlite3
import string
import random
from datetime import datetime

from flask import Flask, request, jsonify, redirect, render_template, g, abort

app = Flask(__name__)

DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "urls.db")
SHORT_CODE_LENGTH = 6
ALPHABET = string.ascii_letters + string.digits


# ----------------------------------------------------------------------------
# Database helpers
# ----------------------------------------------------------------------------
def get_db():
    """Get (or create) a SQLite connection for the current request context."""
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


def init_db():
    """Create the urls table if it doesn't already exist."""
    with sqlite3.connect(DATABASE) as db:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                short_code TEXT UNIQUE NOT NULL,
                original_url TEXT NOT NULL,
                created_at TEXT NOT NULL,
                clicks INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        db.commit()


# ----------------------------------------------------------------------------
# Utility functions
# ----------------------------------------------------------------------------
def generate_short_code(length=SHORT_CODE_LENGTH):
    """Generate a random alphanumeric short code."""
    return "".join(random.choice(ALPHABET) for _ in range(length))


def code_exists(db, code):
    row = db.execute(
        "SELECT 1 FROM urls WHERE short_code = ?", (code,)
    ).fetchone()
    return row is not None


def create_unique_short_code(db):
    """Keep generating codes until we find one that isn't already used."""
    code = generate_short_code()
    while code_exists(db, code):
        code = generate_short_code()
    return code


def is_valid_url(url):
    """Very basic sanity check on the submitted URL."""
    return isinstance(url, str) and url.strip().startswith(("http://", "https://"))


# ----------------------------------------------------------------------------
# Routes
# ----------------------------------------------------------------------------
@app.route("/")
def index():
    """Serve the simple frontend for creating short URLs."""
    return render_template("index.html")


@app.route("/api/shorten", methods=["POST"])
def shorten_url():
    """
    Accepts JSON: { "url": "https://example.com/very/long/path" }
    Optionally accepts a custom code: { "url": "...", "custom_code": "myalias" }
    Returns JSON: { "short_code": "...", "short_url": "...", "original_url": "..." }
    """
    data = request.get_json(silent=True) or request.form

    original_url = (data.get("url") or "").strip()
    custom_code = (data.get("custom_code") or "").strip()

    if not is_valid_url(original_url):
        return jsonify({"error": "Please provide a valid URL starting with http:// or https://"}), 400

    db = get_db()

    if custom_code:
        if not custom_code.isalnum():
            return jsonify({"error": "Custom code must be alphanumeric"}), 400
        if code_exists(db, custom_code):
            return jsonify({"error": "That custom code is already taken"}), 409
        short_code = custom_code
    else:
        short_code = create_unique_short_code(db)

    db.execute(
        "INSERT INTO urls (short_code, original_url, created_at) VALUES (?, ?, ?)",
        (short_code, original_url, datetime.utcnow().isoformat()),
    )
    db.commit()

    short_url = request.host_url.rstrip("/") + "/" + short_code

    return jsonify(
        {
            "short_code": short_code,
            "short_url": short_url,
            "original_url": original_url,
        }
    ), 201


@app.route("/<short_code>")
def redirect_to_original(short_code):
    """Redirect a short code to its original long URL."""
    db = get_db()
    row = db.execute(
        "SELECT original_url FROM urls WHERE short_code = ?", (short_code,)
    ).fetchone()

    if row is None:
        abort(404)

    db.execute(
        "UPDATE urls SET clicks = clicks + 1 WHERE short_code = ?", (short_code,)
    )
    db.commit()

    return redirect(row["original_url"], code=302)


@app.route("/api/urls", methods=["GET"])
def list_urls():
    """Return all shortened URLs (handy for debugging / demo purposes)."""
    db = get_db()
    rows = db.execute(
        "SELECT short_code, original_url, created_at, clicks FROM urls ORDER BY id DESC"
    ).fetchall()
    return jsonify([dict(row) for row in rows])


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Short URL not found"}), 404


if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)
