from django.contrib import admin
from django.apps import apps
from questionnaire.models import Question

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    filter_horizontal = ['options']


# Register your models here.
app = apps.get_app_config('questionnaire')

for model_name, model in app.models.items():
    try:
        admin.site.register(model)
    except:
        pass

