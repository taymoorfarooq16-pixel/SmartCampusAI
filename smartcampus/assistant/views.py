import logging
import os
from difflib import get_close_matches

from google import genai
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Attendance, Event, FAQ, LostItem, Timetable

logger = logging.getLogger(__name__)


def chatbot(request):
    if request.method == "POST" and request.POST.get("clear_chat"):
        request.session.pop("chat", None)
        return redirect("chatbot")

    chat = request.session.get("chat", [])
    if request.method == "POST":
        user_input = request.POST.get("query", "").strip()
        if user_input:
            try:
                api_key = os.environ.get("GEMINI_API_KEY")
                if not api_key:
                    raise RuntimeError("GEMINI_API_KEY is not configured")

                campus_info = "\n".join([
                    "FAQs:\n" + ("\n".join(
                        f"Q: {faq.question}\nA: {faq.answer}"
                        for faq in FAQ.objects.all()[:50]
                    ) or "No FAQs have been added."),
                    "Timetable:\n" + ("\n".join(
                        f"{item.day}: {item.subject} at {item.time}"
                        for item in Timetable.objects.all()[:50]
                    ) or "No timetable has been added."),
                    "Events:\n" + ("\n".join(
                        f"{event.title} on {event.date}"
                        for event in Event.objects.filter(
                            date__gte=timezone.localdate()
                        ).order_by("date")[:50]
                    ) or "No upcoming events have been added."),
                ])
                history = "\n".join(
                    f"Student: {entry.get('user', '')}\nAssistant: {entry.get('bot', '')}"
                    for entry in chat[-6:]
                )
                prompt = f"""You are SmartCampusAI, a helpful campus assistant.
Answer clearly and briefly. Use the campus information below for campus facts.
If the answer is not in that information, say you don't know. Never invent
campus schedules, policies, dates, or events.

{campus_info}

Recent conversation:
{history or "No previous messages."}

Student question: {user_input}
"""

                client = genai.Client(api_key=api_key)
                configured_model = os.environ.get(
                    "GEMINI_MODEL", "gemini-3.5-flash-lite"
                ).strip()
                candidate_models = list(dict.fromkeys([
                    configured_model,
                    "gemini-3.5-flash-lite",
                    "gemini-3.6-flash",
                    "gemini-3.5-flash",
                    "gemini-3.8-flash",
                ]))
                bot_reply = ""
                last_model_error = None
                try:
                    for model_name in candidate_models:
                        try:
                            result = client.models.generate_content(
                                model=model_name,
                                contents=prompt,
                            )
                            bot_reply = (result.text or "").strip()
                            if bot_reply:
                                break
                            last_model_error = RuntimeError(
                                "Gemini returned an empty response"
                            )
                        except Exception as model_error:
                            last_model_error = model_error
                            logger.warning(
                                "Gemini model %s failed; trying a fallback model",
                                model_name,
                                exc_info=True,
                            )
                finally:
                    client.close()

                if not bot_reply:
                    raise RuntimeError(
                        "No Gemini model returned a response"
                    ) from last_model_error
            except Exception:
                logger.exception("SmartCampusAI Gemini request failed")
                questions = [faq.question for faq in FAQ.objects.all()]
                match = get_close_matches(
                    user_input.lower(), questions, n=1, cutoff=0.5
                )
                if match:
                    bot_reply = FAQ.objects.get(question=match[0]).answer
                else:
                    bot_reply = (
                        "The AI service is temporarily unavailable. "
                        "Please try again in a little while."
                    )

            chat.append({"user": user_input, "bot": bot_reply})
            request.session["chat"] = chat[-12:]

    return render(request, "index.html", {"chat": chat})


def attendance_prediction(attended, total):
    current = round((attended / total) * 100, 2) if total > 0 else 0
    if total <= 0:
        return current, ["Attend the next class to start tracking attendance."]

    predictions = []
    a = attended
    t = total
    for i in range(1, 6):
        a += 1
        t += 1
        new_percentage = round((a / t) * 100, 2)
        predictions.append(f"Attend next {i} class(es) → {new_percentage}%")
    return current, predictions


@login_required
def dashboard(request):
    attendance = list(Attendance.objects.filter(student=request.user))
    alerts = []
    for record in attendance:
        current, predictions = attendance_prediction(
            record.attended, record.total
        )
        if current < 75:
            alerts.append({
                "subject": record.subject,
                "current": current,
                "predictions": predictions,
            })

    total_classes = sum(record.total for record in attendance)
    classes_attended = sum(record.attended for record in attendance)
    overall_attendance = (
        round((classes_attended / total_classes) * 100, 2)
        if total_classes > 0 else 0
    )
    upcoming_events = Event.objects.filter(
        date__gte=timezone.localdate()
    ).count()

    return render(request, "dashboard.html", {
        "attendance": attendance,
        "alerts": alerts,
        "overall_attendance": overall_attendance,
        "upcoming_event_count": upcoming_events,
        "attendance_labels": [record.subject for record in attendance],
        "attendance_values": [record.percentage() for record in attendance],
    })


def lostfound(request):
    items = LostItem.objects.all()
    return render(request, "lostfound.html", {"items": items})


def events(request):
    upcoming_events = Event.objects.filter(
        date__gte=timezone.localdate()
    ).order_by("date")
    return render(request, "events.html", {"events": upcoming_events})


def signup_view(request):
    form = UserCreationForm(request.POST or None)
    for field in form.fields.values():
        field.widget.attrs["class"] = "form-control"
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("dashboard")
    return render(request, "signup.html", {"form": form})


def login_view(request):
    error = None
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("dashboard")
        error = "The username or password is incorrect."
    return render(request, "login.html", {"error": error})


@require_POST
def logout_view(request):
    logout(request)
    return redirect("chatbot")
