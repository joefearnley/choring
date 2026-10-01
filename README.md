# choring
Let's do some chores

## Local URLs

- SPA (frontend): `/` (also available at `/app/`)
- API root (DRF): `/api/` — example: `/api/chores/week/`

Run locally:

```bash
.venv/bin/python manage.py runserver
# then open http://127.0.0.1:8000/
```

## Supabase database (local development)

The project uses `db.sqlite3` unless `DATABASE_URL` is set. To use Supabase, create a `.env` file in the project root and set `DATABASE_URL` to the PostgreSQL connection URI from your Supabase dashboard (not the project's `https://` API URL). Use a connection string with SSL enabled (`sslmode=require`); keep the password out of source control. `.env` is ignored by Git.

Install the dependencies after updating `requirements.txt`:

```bash
.venv/bin/pip install -r requirements.txt
```

To copy the existing SQLite data, explicitly clear `DATABASE_URL` for the export so it reads `db.sqlite3`:

```bash
DATABASE_URL='' .venv/bin/python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.permission > data.json
```

Then configure Supabase, create its schema, and import the fixture:

```bash
.venv/bin/python manage.py migrate
.venv/bin/python manage.py loaddata data.json
```

Keep `data.json` private because it contains your application's data, and remove it after verifying the import.
