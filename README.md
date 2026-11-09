# Open Jarvis

Open Jarvis is a small, extensible multi-assistant workspace. It includes a web chat UI, assistant profiles with separate plugin permissions, a plugin registry, and two safe example plugins.

> **Starter scope:** This first version demonstrates the assistant and plugin architecture. It does not call an AI model yet. Add a language-model provider when you are ready for open-ended conversations; current date/time and arithmetic requests work locally without API keys.

## Features

- Three assistant profiles: Jarvis, Dev Assistant, and Work Planner.
- Per-assistant plugin allowlists: the developer assistant can calculate, while the planner can check the time.
- Built-in calculator using a restricted arithmetic AST evaluator (no `eval`).
- Built-in UTC clock/date plugin.
- FastAPI JSON API and a responsive browser-based chat UI.
- Explicit plugin registration: only registered plugins can be invoked.

## Run locally

Requires Python 3.10 or newer.

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open <http://127.0.0.1:8000>. API documentation is available at <http://127.0.0.1:8000/docs>.

## API

- `GET /api/health` — liveness check.
- `GET /api/assistants` — available assistant profiles.
- `GET /api/plugins` — registered plugin manifests.
- `POST /api/chat` — invoke an assistant.

Example request:

```bash
curl -X POST http://127.0.0.1:8000/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"assistant_id":"general","message":"What is 12 * (3 + 4)?"}'
```

## Add a plugin

1. Add a class in `app/plugins/` that subclasses `Plugin` and defines a `PluginManifest`, `matches(message)`, and `run(message)`.
2. Register an instance in `AssistantManager.__init__` in `app/assistant_manager.py`.
3. Add the plugin ID to the `plugin_ids` tuple of only the assistants that should have permission to use it.

Plugins run inside the application process, so only register trusted plugin code. For production use, add authentication, rate limiting, and isolation for plugins that access external systems or user data.

## Project layout

```text
app/
  assistant_manager.py  assistant profiles and permission-aware dispatch
  main.py               FastAPI app and API routes
  plugin_base.py        plugin contract and manifest
  plugins/              built-in plugins
static/                 browser UI
```

## License

MIT. See `LICENSE`.
