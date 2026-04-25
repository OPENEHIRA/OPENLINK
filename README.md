# OpenGuy / OpenClaw

OpenGuy is an AI-powered robotics interface that uses Natural Language to deterministically control hardware via Python.

## Architecture

We have massively simplified and optimized the architecture to be incredibly robust while having zero build steps:

- **Backend:** FastAPI, providing async route handlers, WebSocket connectivity, and local SQLite persistence for command history. It runs directly on your robot or local computer.
- **Frontend:** A single, premium `index.html` file using Tailwind CSS and Vue.js via CDN. This allows it to be hosted *anywhere* (including Vercel natively) without any Node.js `npm build` steps, while retaining real-time communication via WebSockets.

## Running Locally

1. **Install Backend Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the Server:**
   ```bash
   python server.py
   ```
   The backend will serve the single-file UI at `http://localhost:5000` automatically.

## Hosting on Vercel
Because the frontend is a single `index.html` file at the root of the repository, Vercel will deploy it automatically!

Once your Vercel URL is live, open it in your browser and use the **Backend URL** input at the top to point the UI to your local robot's IP or ngrok tunnel (e.g. `http://192.168.1.10:5000`).

## API Key Setup
To enable AI command parsing, set your Anthropic API Key:
- Linux/Mac: `export ANTHROPIC_API_KEY="your-key-here"`
- Windows: `set ANTHROPIC_API_KEY="your-key-here"`
