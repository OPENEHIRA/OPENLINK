# OpenGuy

OpenGuy is an AI-powered robotics interface that uses Natural Language to deterministically control hardware.

## Architecture

We have completely refactored OpenGuy to use a modern, scalable architecture:

- **Backend:** FastAPI, providing async route handlers, WebSocket connectivity, and local SQLite persistence for command history.
- **Frontend:** A decoupled React application built with Vite, Tailwind CSS, Zustand (state management), and Framer Motion (animations).

## Running Locally

1. **Install Backend Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Build the Frontend:**
   ```bash
   cd frontend
   npm install
   npm run build
   cd ..
   ```

3. **Start the Server:**
   ```bash
   python server.py
   ```
   The backend will serve the compiled React app at `http://localhost:5000` automatically.

## API Key Setup
To enable AI command parsing, set your Anthropic API Key:
- Linux/Mac: `export ANTHROPIC_API_KEY="your-key-here"`
- Windows: `set ANTHROPIC_API_KEY="your-key-here"`
