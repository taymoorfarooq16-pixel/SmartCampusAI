from django.db import models
from django.contrib.auth.models import User
from django.db import models

class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()

    def __str__(self):
        return self.question

class Event(models.Model):
    title = models.CharField(max_length=200)
    date = models.DateField()
    description = models.TextField()

    def __str__(self):
        return self.title

class Timetable(models.Model):
    day = models.CharField(max_length=20)
    subject = models.CharField(max_length=100)
    time = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.day} - {self.subject}"
    from django.db import models

class LostItem(models.Model):

    title = models.CharField(max_length=100)

    description = models.TextField()

    image = models.ImageField(upload_to='lost_items/')

    contact = models.CharField(max_length=100)

    def __str__(self):
        return self.title
    from django.contrib.auth.models import User

class Attendance(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    attended = models.IntegerField(default=0)
    total = models.IntegerField(default=0)

    def percentage(self):
        if self.total == 0:
            return 0
        return round((self.attended/self.total)*100, 2)

    def __str__(self):
        return f"{self.student.username} - {self.subject}"