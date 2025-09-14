# Repository Guidelines

## Project Structure & Module Organization
- `src/` — application code (modules, services, UI, routes).
- `tests/` — automated tests mirroring `src/` paths (e.g., `tests/module/test_unit.py`, `tests/module/unit.test.ts`).
- `assets/` — static files (images, styles, data seeds).
- `scripts/` — helper scripts for local dev/CI.
- `.env` / `.env.example` — environment configuration (never commit secrets).
- `dist/` or build artifacts may be generated; do not edit checked‑in outputs.

## Build, Test, and Development Commands
This repo may use Node.js or Python. Use the stack that matches the code in your folder (look for `package.json` or `requirements.txt`).
- Node.js:
  - `npm i` — install dependencies.
  - `npm run dev` — start local dev server/watchers.
  - `npm test` — run unit tests.
  - `npm run build` — production build to `dist/`.
- Python:

  - `python -m venv .venv && . .venv/bin/activate` (Windows: `.venv/Scripts/activate`).
  - `pip install -r requirements.txt` — install dependencies.
  - `pytest -q` — run tests.
  - `python -m <entrypoint>` or `flask run` / `uvicorn app:app --reload` — run locally.

## Coding Style & Naming Conventions
- Favor readability and existing patterns.
- Indentation: 2 spaces (JS/TS); 4 spaces (Python).
- Naming: `camelCase` (functions/vars), `PascalCase` (classes), `CONSTANT_CASE` (constants), `snake_case` (Python modules).
- Formatters/Linters: use configured tools (`prettier`, `eslint`, `black`, `flake8`). Run before pushing.

## Testing Guidelines
- Place tests under `tests/` mirroring `src/` structure.
- Use the configured runner (e.g., Jest/Vitest for Node, Pytest for Python).
- Focus on core flows and edge cases; mark slow/integration tests.
- Name tests clearly (e.g., `test_<unit>.py`, `<unit>.test.ts`).

## Commit & Pull Request Guidelines
- Use Conventional Commits: `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`.
- Keep messages imperative and scoped (e.g., `fix(auth): handle token refresh`).
- PRs should include: purpose, setup/testing notes, linked issues (e.g., `Closes #123`), and screenshots for UI changes.
- Keep PRs focused and small.

## Security & Configuration
- Never commit secrets; provide safe defaults in `.env.example`.
- Validate and sanitize external input; avoid logging sensitive data.
- Prefer well‑maintained dependencies; review updates periodically.

## Agent‑Specific Notes (Codex CLI)
- Respect this AGENTS.md across the repo scope.
- Make minimal, focused changes; follow existing style.
- Prefer `scripts/` entries for reproducible tasks and CI.
