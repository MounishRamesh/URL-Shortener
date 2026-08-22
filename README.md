# Simple URL Shortener

A minimal URL shortener built with **Flask** and **SQLite**.

## Features

- `POST /api/shorten` — submit a long URL (and optionally a custom alias) and get back a short code.
- `GET /<short_code>` — redirects to the original long URL, and tracks click count.
- `GET /api/urls` — lists all shortened URLs (for the demo table on the frontend).
- Basic web frontend (`/`) to create and view short links.
- Data persisted in a local SQLite database file (`urls.db`), created automatically on first run.

## Live Demo

🔗 [Click here](https://url-shortener-msqq.onrender.com/) to try it out.

## Project structure

```
url-shortener/
├── app.py                 # Flask app: routes, DB logic, redirect logic
├── requirements.txt        # Python dependencies
├── templates/
│   └── index.html          # Frontend page
├── static/
│   └── style.css           # Frontend styling
└── urls.db                 # SQLite DB (auto-created on first run)
```

## Setup

1. Create a virtual environment (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate      # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:
   ```bash
   python app.py
   ```

4. Open your browser at `http://localhost:5000`

The SQLite database (`urls.db`) is created automatically the first time the app runs.

## API usage

### Shorten a URL

```bash
curl -X POST http://localhost:5000/api/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.example.com/some/very/long/path?query=123"}'
```

Response:
```json
{
  "short_code": "aZ3xQ1",
  "short_url": "http://localhost:5000/aZ3xQ1",
  "original_url": "https://www.example.com/some/very/long/path?query=123"
}
```

### Use a custom alias

```bash
curl -X POST http://localhost:5000/api/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.example.com", "custom_code": "mysite"}'
```

### Visit the short URL

Open `http://localhost:5000/aZ3xQ1` in a browser — it will 302-redirect to the original URL.

### List all URLs

```bash
curl http://localhost:5000/api/urls
```

## Notes / possible extensions

- Add expiration dates for short links.
- Add rate limiting to prevent abuse.
- Switch to PostgreSQL/MongoDB for production use.
- Add user accounts so people can manage their own links.
- Add analytics (referrers, geo-location of clicks, etc.).
