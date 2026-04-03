# OpenGuy

**Control a robot with plain English.**

OpenGuy converts natural language commands into structured robot actions — no robotics experience required. Type what you want the arm to do, and OpenGuy parses your intent, scores its confidence, and executes the response.

> **Status:** Active development · AI parser live · Web UI ready · Hardware integration in progress

---

## Demo

```
Input   →  "go a bit forward"
Parsed  →  { "action": "move", "direction": "forward", "distance_cm": 5, "confidence": 0.92 }
Output  →  Moving forward 5 cm... ✓

Input   →  "turn slightly right"
Parsed  →  { "action": "rotate", "direction": "right", "angle_deg": 15, "confidence": 0.88 }
Output  →  Rotating right 15°... ✓

Input   →  "pick up the object"
Parsed  →  { "action": "grab", "confidence": 0.95 }
Output  →  Closing gripper... ✓
```

The web UI displays parsed JSON, a live confidence bar, and the simulated robot response — all in one view. Previous commands appear as clickable chips so you can re-run them instantly.

---

## Features

- **Natural language control** — describe actions conversationally, no syntax to learn
- **AI-powered parser** — Llama 3.1 via Groq interprets flexible, vague phrasing accurately
- **Regex fallback** — automatically switches to a pattern-based parser when the AI is unreachable, so the system always works
- **Confidence scoring** — every parsed command carries a confidence value; low-confidence results are flagged visually
- **Command history** *(new)* — previously run commands appear as one-click chips in the UI, making iteration fast
- **Quick action buttons** *(new)* — common commands are pre-loaded as suggestion chips so new users can explore immediately
- **Zero-setup web UI** — open `index.html` in any browser and start typing

---

## How It Works

**1. AI Parser**
Each command is sent to Llama 3.1 (via Groq's free API) with a structured system prompt. The model returns a clean JSON object — action, direction, distance, angle, and a confidence score. Vague phrasing like "a bit" or "slightly" is estimated automatically rather than rejected.

**2. Regex Fallback**
If the AI is unreachable, OpenGuy silently switches to a regex parser. Common command patterns are matched reliably, and the result is marked with a lower confidence score so you always know which path was taken.

**3. Simulator**
The parsed command is passed to a simulator that describes the robot's response in plain text — motor engagement, force applied, confirmation. This layer is designed to be swapped for real hardware output when the time comes.

---

## Try It

**Web UI (no setup)**

Open `index.html` in any browser. Enter your [Groq API key](https://console.groq.com) once via the top-right menu — it saves locally and is never sent anywhere else. Type a command or tap one of the suggestion chips to get started.

**Command line**

```bash
git clone https://github.com/NEHIRAAS/openguy.git
cd openguy
python main.py
```

Requirements: Python 3.8+, no external libraries.

---

## What's New

**Command history + quick actions (latest release)**

The web UI now remembers your previous commands and surfaces them as clickable chips below the input. Tap any past command to re-run it instantly — no retyping required. A set of pre-loaded quick action buttons also makes it easier for new users to explore what OpenGuy understands without guessing at syntax. Both features are purely frontend; no backend changes were required.

---

## Project Structure

```
openguy/
├── index.html      # Web UI — single file, no build step
├── main.py         # CLI entry point
├── parser.py       # AI parser + regex fallback
└── simulator.py    # Simulates robot arm responses
```

Four files. Intentionally minimal. Every part is straightforward to read and extend.

---

## Roadmap

- [x] AI-based natural language parser
- [x] Regex fallback with confidence scoring
- [x] Web UI (single-file, no setup)
- [x] Command history + quick action chips
- [ ] Serial/USB connection to real hardware
- [ ] Multi-step command chains ("pick up the block and move it left")
- [ ] WhatsApp / Telegram bot interface
- [ ] Voice input via browser microphone
- [ ] PyBullet physics simulation

Have an idea? [Open an issue](https://github.com/NEHIRAAS/openguy/issues) — suggestions are welcome.

---

## Contributing

OpenGuy is beginner-friendly. If you can write Python or basic HTML, you can contribute.

Good places to start:

- Add new command types or improve edge-case handling in `parser.py`
- Improve the AI system prompt for better accuracy on ambiguous input
- Write tests for the `parse()` function
- Connect `simulator.py` to real serial hardware
- Improve documentation or add usage examples

**How to contribute:**

1. Fork the repo
2. Create a branch: `git checkout -b your-feature`
3. Make your changes
4. Open a pull request with a short description

No contribution is too small.

---

## Support

If OpenGuy is useful to you, a star helps others find it.

[⭐ Star on GitHub](https://github.com/NEHIRAAS/openguy)

---

## License

MIT — free to use, modify, and distribute.

---

*Built by [@NEHIRAAS](https://github.com/NEHIRAAS)*
