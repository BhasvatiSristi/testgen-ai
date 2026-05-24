# TestGen AI

An AI-powered test case generation skeleton using the Mistral AI API.

## Setup

1. Create a virtual environment and install dependencies:

```bash
pip install -r requirements.txt
```

2. Set your Mistral API key in `.env`:

```bash
MISTRAL_API_KEY=your_key_here
```

3. Run the Streamlit app:

```bash
streamlit run frontend/app.py
```

## How it works

- Paste an OpenAPI/Swagger document or a plain-English requirement.
- The backend parses the input, builds a prompt-ready context, and sends a two-shot request to Mistral.
- The app displays unit, integration, and edge-case outputs separately.
