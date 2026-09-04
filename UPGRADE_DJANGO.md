Upgrade summary

- Upgraded Django from 1.11 → 2.2 → 3.2 → 4.2 → 5.2
- Upgraded Django REST Framework to 3.18 to match Django 5.x

Files changed

- Updated dependencies: requirements.txt
- Fixed URL pattern usage: choring/urls.py (replaced deprecated `url()` import with `path()`)

Commands used (reproduce locally):

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip setuptools wheel
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py check
.venv/bin/python manage.py runserver
```

Notes / Next steps

- There are no unit tests in `choring/chores/tests.py` — consider adding tests to catch regressions.
- Review `settings.py` for deprecated settings (e.g. `USE_L10N`) and remove/adjust if needed for future Django releases.
- Run the application and full integration tests to ensure runtime behavior.
