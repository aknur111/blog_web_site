# Cosmic Blog — Final Project (Advanced Databases, NoSQL)

Quick start (short):
1. Start MongoDB
   - Docker: `docker run -d -p 27017:27017 --name mongo mongo:6.0`
   - Or local service (make sure MongoDB is running)

2. Install Python deps
   - `python3 -m venv .venv && source .venv/bin/activate`
   - `pip install -r requirements.txt`

3. Run backend
   - `uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000`
   - Backend will create recommended indexes on startup.

4. Serve frontend (recommended to avoid CORS/file issues)
   - From project root: `cd frontend && python3 -m http.server 5500`
   - Open `http://localhost:5500/index.html`

Notes on API_BASE:
- If frontend and backend served from different origins (e.g. frontend on port 5500, backend on 8000), set API base to backend in the frontend:
  - Edit `frontend/app.js` or set `window.__API_BASE__ = 'http://localhost:8000/api'` before the script loads.
- The app also auto-detects `file://` and defaults to `http://localhost:8000/api`.

Quick register & create post (curl):
- Register (get token):
  - `curl -X POST "http://localhost:8000/api/register?username=me&email=me@example.com"`
- Create post:
  - `curl -X POST "http://localhost:8000/api/posts" -H "Authorization: Bearer <token>" -H "Content-Type: application/json" -d '{"author_id":"me","content":"Title\n\nBody","media_url":"","category_id":"general","status":"published","tags":["demo"]}'`

Troubleshooting:
- If fetch fails, check browser DevTools → Network for request URL and response.
- If you see CORS errors, confirm backend running and CORS middleware enabled (it is by default).
- Check backend logs for stack traces and Mongo connectivity issues.

See code for API details and endpoints. Если нужно — подготовлю файл .env.example и скрипты запуска.
