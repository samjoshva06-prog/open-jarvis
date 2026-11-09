# Open Jarvis

Open Jarvis is a multi-assistant workspace combining optional AI chat with local productivity plugins. Assistant profiles have separate plugin permissions. The app runs without an AI key for local tools; configure an OpenAI-compatible Chat Completions provider for open-ended conversations.

## Features

- Three assistant profiles: Jarvis, Dev Assistant, and Work Planner.
- Optional AI chat through an OpenAI-compatible `/chat/completions` endpoint.
- Conversation context is sent with each request and kept in the browser for the active page only.
- Local SQLite task list: add, list, and complete tasks; optional due-date text is supported.
- Built-in calculator using a restricted arithmetic AST evaluator (no `eval`).
- Built-in UTC clock/date plugin.
- Per-assistant plugin allowlists and a responsive browser UI.

## Run locally

Requires Python 3.10 or newer.

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open <http://127.0.0.1:8000>. API documentation is available at <http://127.0.0.1:8000/docs>.

## Enable AI conversations

Set your provider configuration in the server environment. The API key remains on the server and is never sent to the browser.

```bash
export OPENAI_API_KEY="your-api-key"
# Optional: defaults shown
export OPENAI_BASE_URL="https://api.openai.com/v1"
export OPENAI_MODEL="gpt-4o-mini"
uvicorn app.main:app --reload
```

`OPENAI_BASE_URL` can point to another trusted service that implements the OpenAI Chat Completions API. Do not configure an endpoint you do not trust. Keep credentials out of source control. The provider receives chat messages when AI is enabled; avoid sending sensitive data unless you have reviewed the provider's privacy terms.

## Productivity commands

Use the Planner or Jarvis assistant and enter commands such as:

- `add task: prepare project plan`
- `add task: send proposal | due: 2026-12-01`
- `list tasks`
- `complete task 1`

Tasks are stored in `data/open_jarvis.sqlite3` by default. Override the location with `OPEN_JARVIS_DATABASE`. Due dates are stored as user-provided text; this version does not send notifications or calendar events.

## API

- `GET /api/health` — liveness and AI configuration status.
- `GET /api/assistants` — available assistant profiles.
- `GET /api/plugins` — registered plugin manifests.
- `POST /api/chat` — invoke an assistant with optional recent conversation history.

Example request:

```bash
curl -X POST http://127.0.0.1:8000/api/chat \\
  -H 'Content-Type: application/json' \\
  -d '{"assistant_id":"general","message":"What is 12 * (3 + 4)?"}'
```

## Add a plugin

1. Add a class in `app/plugins/` that subclasses `Plugin` and defines a `PluginManifest`, `matches(message)`, and `run(message)`.
2. Register an instance in `AssistantManager.__init__` in `app/assistant_manager.py`.
3. Add the plugin ID to the `plugin_ids` tuple of only the assistants that should have permission to use it.

Plugins execute inside the application process, so only register trusted plugin code. For production use, add authentication, rate limiting, database backups, and isolation for plugins that access external systems or user data. The included SQLite store is for a single local instance, not multi-user deployment.

## Project layout

```text
app/
  ai_provider.py        OpenAI-compatible provider client
  assistant_manager.py  assistant profiles and permission-aware routing
  main.py               FastAPI app and API routes
  plugin_base.py        plugin contract and manifest
  plugins/              calculator, clock, and local task manager
static/                 browser chat UI
```

## License

MIT. See `LICENSE`.
