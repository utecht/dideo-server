"""cafe URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from questionnaire.views import *
from rest_framework import routers
from rest_framework.authtoken import views

admin.autodiscover()

router = routers.DefaultRouter()
router.register(r'categories', CategoryList)
router.register(r'questions/(?P<category>[0-9]+)', QuestionList)
router.register(r'answer', AnswerViewSet)
router.register(r'user', UserView, base_name='user')
router.register(r'definitions', DefinitionList, base_name='d')

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^admin/', admin.site.urls),
    url(r'^auth/', views.obtain_auth_token),
    url(r'^new_survey/', NewSurveyView.as_view()),
]
