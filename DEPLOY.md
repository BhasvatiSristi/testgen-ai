# Deployment Guide — Netlify (frontend) + Replit (backend)

This repository contains a Vite + Vue frontend at `frontend/web` and a FastAPI backend at `backend`.

Quick local run
- Backend:
```
python -m venv .venv
source .venv/Scripts/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.api:app --reload
```

- Frontend:
```
cd frontend/web
npm install
npm run dev
```

Deploy frontend to Netlify (recommended)
1. Create a Git repository and push this project to GitHub (or Git provider supported by Netlify).
2. In Netlify, click "New site from Git" and connect your repository.
3. In the build settings use:
   - Build command: `npm install && npm run build`
   - Publish directory: `dist`
4. (Optional) Add environment variables in Netlify if needed.
Netlify will run the build and publish the static site from `frontend/web/dist`.

Alternatively, you can drag-and-drop the contents of `frontend/web/dist` into Netlify's deploy panel after running `npm run build` locally.

Deploy backend to Replit
1. Create a Replit account and choose "Import from GitHub" (or create a new Repl and connect the repo).
2. Replit will detect `requirements.txt`. Ensure the run command is set to `bash start.sh` in the Repl settings (this repo includes a `.replit` file which sets that).
3. Replit exposes your app on a public URL. The `start.sh` script uses the provided `$PORT` if Replit sets it.

Notes and tips
- If you deploy backend separately, update the frontend API base URL in `frontend/web/src/lib/api.js` (or where requests are made) to point at the Replit URL (including `/api`).
- For GitHub Pages (frontend) use a different workflow — Netlify is simpler for Vite apps.
- If you prefer a container-based deploy (Fly/Railway), I can add a `Dockerfile` and configs.

If you want, I can:
- Create a GitHub Actions workflow to build and publish the frontend to GitHub Pages or Netlify.
- Add a `Dockerfile` and sample `fly.toml` for container deploy.
