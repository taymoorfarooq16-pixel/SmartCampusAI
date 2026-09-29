# Smart Campus AI

A Django-based Smart Campus Management System with:

- Student Dashboard
- Attendance Tracking and percentage predictions
- Timetable and event listings
- Lost & Found Portal
- FAQ Chat Assistant

## Technologies Used

- Python
- Django
- SQLite for local development and PostgreSQL when hosted
- HTML
- CSS
- Bootstrap

The current chatbot matches student questions against saved FAQs; it does not call an external AI model yet.

## Run locally

Open a terminal in the `smartcampus` folder, then run:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
py manage.py migrate
py manage.py runserver
```

Open `http://127.0.0.1:8000` in your browser.

## Deploy on Render

Connect this GitHub repository as a Python web service and set its **Root Directory** to `smartcampus`.

- Build command: `pip install -r requirements.txt && python manage.py collectstatic --no-input && python manage.py migrate`
- Start command: `gunicorn smartcampus.wsgi:application`
- Add `SECRET_KEY` as a generated secret environment variable.
- Add `DATABASE_URL` with the PostgreSQL connection string you choose for the app.
- Set `DEBUG` to `false`.

The project uses local SQLite when `DATABASE_URL` is empty, which is suitable for local learning. Use PostgreSQL for a hosted app so its accounts and campus records persist across deploys.

The lost-and-found image uploads use local disk storage. Render's free web service does not preserve uploaded files across deploys, so uploaded images need a separate media storage service for long-term use.

## Developed By

Taymoor Farooq
B.Tech CSE
This change was made in feature-demo branch.
