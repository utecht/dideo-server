from questionnaire.models import *
from questionnaire.serializers import *
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework import permissions
from django.db.models import Q

# Create your views here.
class CategoryList(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
class QuestionList(viewsets.ReadOnlyModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    authentication_classes = (TokenAuthentication,)

    def list(self, request, category):
        if request.user.is_authenticated():
            print(request.user)
            questions = Question.objects.filter(category=category)
            for q in questions:
                q.answer = Answer.objects.filter(user=request.user, question=q)
        else:
            questions = Question.objects.filter(category=category).order_by('order')
        serializer = self.get_serializer(questions, many=True)
        return Response(serializer.data)

class AnswerAccessPermission(permissions.BasePermission):
    message = 'Must be logged in to submit answers'

    def has_permission(self, request, view):
        return request.user is not None

    def has_object_permission(self, request, view, obj):
        self.message = "You can only modify your own answers"
        return obj.user == request.user
        

class AnswerViewSet(viewsets.ModelViewSet):
    serializer_class = AnswerSerializer
    queryset = Answer.objects.all()
    permission_classes = (AnswerAccessPermission,)
    authentication_classes = (TokenAuthentication,)
    lookup_fields = ('question', 'user')

    def perform_create(self, serializer):
        Answer.objects.filter(user=self.request.user, question=serializer.validated_data['question']).delete()
        serializer.save(user=self.request.user)
        
    def perform_update(self, serializer):
        serializer.save(user=self.request.user)
