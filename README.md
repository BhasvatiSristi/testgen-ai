# TestGen AI

An AI-powered test case generation app using a Vue frontend and the existing Mistral-based Python backend.

## Setup

1. Install the Python backend dependencies:

```bash
pip install -r requirements.txt
```

2. Set your Mistral API key in `.env`:

```bash
MISTRAL_API_KEY=your_key_here
```

3. Start the API server:

```bash
uvicorn backend.api:app --reload --port 8000
```

4. Install and run the Vue frontend:

```bash
cd frontend/web
npm install
npm run dev
```

## How it works

- Paste an OpenAPI/Swagger document or a plain-English requirement.
- The backend parses the input, builds a prompt-ready context, and sends a two-shot request to Mistral.
- The Vue UI shows unit, integration, and edge-case outputs, coverage estimates, gap suggestions, history, and export actions.
