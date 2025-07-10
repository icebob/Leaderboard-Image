# Copilot Instructions for Leaderboard-Image

## Project Overview
- **Leaderboard-Image** is a Flask web app for comparing and ranking AI-generated images from multiple models using ELO scoring.
- The app supports Arena Battle (blind voting), Side-by-Side comparison, Leaderboard, and ELO history graph modes.
- Images and prompts are organized in `data/<prompt_id>/`, with flexible file extensions for model outputs.
- Model metadata and configuration are managed in `config.py`.

## Key Components
- `app.py`: Main Flask app, API endpoints, voting logic, ELO updates, and static file serving.
- `database.py`: Database connection, schema initialization, and ELO update logic.
- `config.py`: Model list, allowed file extensions, and app settings.
- `data/`: Contains prompt folders, each with a `prompt.txt` and images for each model.
- `templates/` and `static/`: Frontend assets (HTML, JS, CSS).

## Developer Workflows
- **Install dependencies:** `pip install -r requirements.txt`
- **Initialize DB:** `python database.py`
- **Run app (dev):** `python app.py` or `flask run --host=0.0.0.0`
- **Reset votes/ELO:** `python app.py reset-votes`
- **Add new models:** Update `MODELS` in `config.py` and add images to each prompt folder.
- **Add new prompts:** Create a new folder in `data/` with a `prompt.txt` and model images.

## Project-Specific Patterns
- **Image lookup:** Use the model's `filename` (from `config.py`) and match any allowed extension in the prompt folder.
- **Blind voting:** Model names are hidden until after voting in Arena Battle mode.
- **API endpoints:** All data for frontend is served via `/api/*` endpoints (see `app.py`).
- **ELO logic:** ELO scores are updated and tracked in both `model_elo` and `elo_history` tables.
- **Prompt caching:** Prompt IDs are cached and refreshed on app start or in debug mode.

## Conventions & Tips
- Only use file extensions listed in `ALLOWED_EXTENSIONS` from `config.py`.
- Model IDs and filenames must match across config, DB, and data folders.
- Use `send_from_directory` for serving files to avoid path traversal issues.
- For DB schema, see the `README.md` or `database.py` for table definitions.
- For frontend changes, update `templates/` and `static/` as needed.

## Example: Adding a New Model
1. Add entry to `MODELS` in `config.py`:
   ```python
   'model-999': {'name': 'New Model', 'filename': 'newmodel', 'open_source': True},
   ```
2. Add `newmodel.jpg/png/webp` to each `data/<prompt_id>/` folder.
3. Restart the app to refresh prompt/model lists.

## References
- See `README.md` for user-facing documentation and DB schema.
- See `docs/index.html` for detailed documentation.

---
For questions or unclear conventions, check `README.md` or ask for clarification.
