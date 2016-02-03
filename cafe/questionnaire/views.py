from questionnaire.models import *
from questionnaire.serializers import *
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.response import Response

# Create your views here.
class CategoryList(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
class QuestionList(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

    def list(self, request, category):
        questions = Question.objects.filter(category=category)
        serializer = self.get_serializer(questions, many=True)
        return Response(serializer.data)

