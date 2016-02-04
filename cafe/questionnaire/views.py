from questionnaire.models import *
from questionnaire.serializers import *
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Q

# Create your views here.
class CategoryList(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
class QuestionList(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

    def list(self, request, category):
        if request.user.is_authenticated():
            questions = Question.objects.filter(
                    Q(category=category),
                    Q(answer__isnull=True) | Q(answer__user=request.user)
                ).order_by('order')
        else:
            questions = Question.objects.filter(category=category).order_by('order')
        serializer = self.get_serializer(questions, many=True)
        return Response(serializer.data)

class AnswerAccessPermission(permissions.BasePermission):
    message = 'Must be logged in to submit answers'

    def has_permission(self, request, view):
        return request.user

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
        

class AnswerViewSet(viewsets.ModelViewSet):
    serializer_class = AnswerSerializer
    queryset = Answer.objects.all()
    permission_classes = (permissions.IsAdminUser, AnswerAccessPermission)
