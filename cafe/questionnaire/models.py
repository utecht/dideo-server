from django.db import models
from django.contrib.auth.models import User
# imports for user token creation
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.core.management import call_command
import re

# Create your models here.
class Definition():
    def __init__(self, word, definition):
        self.word = word
        self.definition = definition

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    order = models.IntegerField()
    def __str__(self):
        return self.name

QUESTION_TYPES = (('combo', 'Combo Box'),
                  ('check', 'Check Boxes'),
                  ('drugs', 'Drugs'),
                  ('text', 'Text Field'),
                  ('int', 'Integer Field'),
                  ('bool', 'Yes or No'))
    
class Question(models.Model):
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    text = models.TextField(blank=False)
    order = models.IntegerField()
    q_type = models.CharField(max_length=5, choices=QUESTION_TYPES)
    options = models.ManyToManyField('Option', blank=True)
    tags = models.CharField(max_length=100, blank=True, null=True)
    help_text = models.CharField(max_length=500, blank=True, null=True)
    depends_on = models.ManyToManyField('Question', blank=True)

    def disabled(self, survey):
        if survey.user.is_authenticated():
            for question in self.depends_on.all():
                for answer in question.answer.filter(survey=survey):
                    if answer.yesno == False:
                        return True
        return False

    def __str__(self):
        return "{} - {}".format(self.id, self.text[:100])

    def only_text(self):
        return re.sub(r'<([^>]+)\|([^>]+)>', '\\1', self.text)


class Option(models.Model):
    text = models.CharField(max_length=200)
    free = models.BooleanField(default=False)
    def __str__(self):
        return self.text

class Survey(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return "{} - {}".format(self.user, self.id)

class Answer(models.Model):
    text = models.CharField(max_length=50, null=True, blank=True)
    options = models.ManyToManyField('Option', blank=True)
    question = models.ForeignKey('Question', on_delete=models.CASCADE, related_name='answer')
    integer = models.IntegerField(null=True, blank=True)
    yesno = models.NullBooleanField(null=True, blank=True)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('survey', 'question')
    def __str__(self):
        return "{} - {}".format(self.survey, self.question.id)

class Statement(models.Model):
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    predicate = models.CharField(max_length=255)
    obj = models.CharField(max_length=255)
    choice = models.ForeignKey('Option', on_delete=models.CASCADE, null=True, blank=True)
    value = models.BooleanField()
    def __str__(self):
        return "{} - {} {} {}".format(self.question, self.subject, self.predicate, self.obj)

class RDFPrefix(models.Model):
    short = models.CharField(max_length=10)
    full = models.CharField(max_length=255)
    def __str__(self):
        return "{}:{}".format(self.short, self.full)

    
# Create user tokens
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

@receiver(post_save, sender=Statement)
def generate_graphs(sender, instance=None, created=False, **kwargs):
    if instance:
        call_command('generate_graphs', str(instance.question.id), verbosity=0)

@receiver(post_save, sender=Answer)
def add_rdf(sender, instance=None, created=False, **kwargs):
    if instance:
        print('Need to add RDF')
        print(instance)
