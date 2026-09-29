# SmartCampusAI

SmartCampusAI is a Django web app for campus information and student tools. Its chat assistant uses Gemini and answers campus questions from records that an administrator adds to the database.

## Features

- Student sign-up and login
- Student dashboard with attendance totals and per-subject chart
- Attendance alerts and predictions
- Upcoming campus events
- Lost and found listings
- Gemini campus assistant grounded in saved FAQs, timetable entries, and upcoming events
- FAQ matching fallback when the AI service cannot be reached

The project starts with an empty campus database. The assistant will say when information has not been added, rather than invent campus facts.

## Run locally on Windows

Open PowerShell in the `smartcampus` folder:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Open `.env` in VS Code. Set a private `SECRET_KEY` and add your Gemini API key to `GEMINI_API_KEY`. Leave `DATABASE_URL` empty to use local SQLite. The `.env` file is ignored by Git and must never be committed.

Then run:

```powershell
py manage.py migrate
py manage.py createsuperuser
py manage.py runserver
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). Use the admin account at `/admin/` to add FAQs, timetable entries, events, attendance records, and lost items. The chatbot needs saved campus information to answer campus-specific questions.

## Deploy on Render

The GitHub repository is connected to the Render web service. Its settings should use:

- **Root Directory:** `smartcampus`
- **Build Command:** `pip install -r requirements.txt && python manage.py collectstatic --no-input && python manage.py migrate`
- **Start Command:** `gunicorn smartcampus.wsgi:application`

Set these environment variables in the Render service:

| Variable | Value |
| --- | --- |
| `SECRET_KEY` | A unique generated secret |
| `DEBUG` | `false` |
| `DATABASE_URL` | Your PostgreSQL connection URL |
| `GEMINI_API_KEY` | Your Gemini API key |
| `GEMINI_MODEL` | Optional; defaults to `gemini-3.5-flash-lite` |

Never put real secrets in this repository. After deployment, create an administrator account through the Render Shell with `python manage.py createsuperuser`, then open `/admin/` on the deployed site and add your campus data.

## Deployment notes

- A free Render instance may sleep when idle, so the first request after a pause can take longer.
- Files uploaded to the service's local media folder are not durable across redeploys. Use persistent or external media storage if lost-and-found images must be kept.
