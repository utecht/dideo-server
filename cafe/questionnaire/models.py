from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.name

QUESTION_TYPES = (('combo', 'Combo Box'),
                  ('check', 'Check Boxes'),
                  ('text', 'Text Field'),
                  ('int', 'Integer Field'),
                  ('bool', 'Yes or No'))
    
class Question(models.Model):
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    text = models.CharField(max_length=200, blank=False)
    order = models.IntegerField()
    q_type = models.CharField(max_length=5, choices=QUESTION_TYPES)
    options = models.ManyToManyField('Option', blank=True)
    def __str__(self):
        return self.text[:50]

class Option(models.Model):
    text = models.CharField(max_length=50)
    free = models.BooleanField(default=False)
    def __str__(self):
        return self.text

class Answer(models.Model):
    text = models.CharField(max_length=50, null=True, blank=True)
    check = models.CommaSeparatedIntegerField(max_length=20, blank=True, null=True)
    question = models.ForeignKey('Question', on_delete=models.CASCADE, related_name='answer')
    number = models.IntegerField(null=True, blank=True)
    yesno = models.NullBooleanField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return "{} - {}".format(self.user, self.question.id)

