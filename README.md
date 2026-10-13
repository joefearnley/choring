# choring
Let's do some chores

## Local URLs

- SPA (frontend): `/` (also available at `/app/`)
- API root (DRF): `/api/` — example: `/api/chores/week/`

## Local setup

Create a virtual environment and install the project requirements:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Run the development server:

```bash
.venv/bin/python manage.py runserver
# then open http://127.0.0.1:8000/
```

Set `ALLOWED_HOSTS` in the root `.env` file as a comma-separated list of hostnames. For local development, use `ALLOWED_HOSTS=localhost,127.0.0.1`; add your deployment hostnames when deploying.

## Database Setup

The project uses SQLite at `db.sqlite3` for local development. Create or update the database schema with:

```bash
.venv/bin/python manage.py migrate
```
