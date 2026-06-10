from .models import Attendance
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .models import LostItem
from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from .models import FAQ, Timetable, Event

def chatbot(request):
    response = ""

    if request.method == "POST":
        user_input = request.POST.get('query').lower()

        # FAQ matching
        faqs = FAQ.objects.all()
        for faq in faqs:
            if faq.question.lower() in user_input:
                response = faq.answer
                break

        # Timetable
        if "timetable" in user_input:
            data = Timetable.objects.all()
            response = "\n".join([f"{t.day}: {t.subject} at {t.time}" for t in data])

        # Events
        if "event" in user_input:
            events = Event.objects.all()
            response = "\n".join([f"{e.title} on {e.date}" for e in events])

        if response == "":
            response = "Sorry, I don't understand."

    return render(request, 'index.html', {'response': response})
def chatbot(request):
    if 'chat' not in request.session:
        request.session['chat'] = []

    chat = request.session['chat']

    if request.method == "POST":
        user_input = request.POST.get('query').lower()
        response = "Sorry, I don't understand."

        from .models import FAQ, Timetable, Event

        for faq in FAQ.objects.all():
            if faq.question.lower() in user_input:
                response = faq.answer

        if "timetable" in user_input:
            data = Timetable.objects.all()
            response = "\n".join([f"{t.day}: {t.subject} at {t.time}" for t in data])

        if "event" in user_input:
            events = Event.objects.all()
            response = "\n".join([f"{e.title} on {e.date}" for e in events])

        chat.append({"user": user_input, "bot": response})
        request.session['chat'] = chat

    return render(request, 'index.html', {"chat": chat})
from difflib import get_close_matches

def chatbot(request):
    if 'chat' not in request.session:
        request.session['chat'] = []

    chat = request.session['chat']

    if request.method == "POST":
        user_input = request.POST.get('query').lower()
        response = "Sorry, I don't understand."

        from .models import FAQ

        questions = [faq.question for faq in FAQ.objects.all()]
        match = get_close_matches(user_input, questions, n=1, cutoff=0.5)

        if match:
            faq = FAQ.objects.get(question=match[0])
            response = faq.answer

        chat.append({"user": user_input, "bot": response})
        request.session['chat'] = chat

    return render(request, 'index.html', {"chat": chat})
def attendance_prediction(attended, total):

    current = round((attended / total) * 100, 2)

    predictions = []

    a = attended
    t = total

    for i in range(1, 6):

        a += 1
        t += 1

        new_percentage = round((a / t) * 100, 2)

        predictions.append(
            f"Attend next {i} class(es) → {new_percentage}%"
        )

    return current, predictions


@login_required
def dashboard(request):

    attendance = Attendance.objects.filter(
        student=request.user
    )

    alerts = []

    for a in attendance:

        current, predictions = attendance_prediction(
    a.attended,
    a.total
)

        if current < 75:

            alerts.append({
    "subject": a.subject,
    "current": current,
    "predictions": predictions
})

    context = {
        "attendance": attendance,
        "alerts": alerts
    }

    return render(
        request,
        "dashboard.html",
        context
    )

def lostfound(request):

    items = LostItem.objects.all()

    return render(request, 'lostfound.html', {'items': items})

def events(request):
    return render(request, 'events.html')
def signup_view(request):

    if request.method == "POST":

        username = request.POST['username']
        password = request.POST['password']

        user = User.objects.create_user(
            username=username,
            password=password
        )

        login(request, user)

        return redirect('/')

    return render(request, 'signup.html')
def login_view(request):

    if request.method == "POST":

        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect('/dashboard/')

    return render(request, 'login.html')
def logout_view(request):

    logout(request)

    return redirect('/')
