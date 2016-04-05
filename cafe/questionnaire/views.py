from questionnaire.models import *
from questionnaire.serializers import *
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework import permissions
from questionnaire.rdf import get_definitions, delete_context, run_statements


# Create your views here.
class DefinitionList(viewsets.ViewSet):
    def list(self, request):
        words = get_definitions()
        if words:
            serializer = DefinitionSerializer(words, many=True)
            return Response(serializer.data)
        else:
            return Response()

class CategoryList(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
class QuestionList(viewsets.ReadOnlyModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    authentication_classes = (TokenAuthentication,)

    def list(self, request, category):
        print(request.user)
        questions = Question.objects.filter(category=category).order_by('id')
        for q in questions:
            if request.user.is_authenticated():
                q.answer = Answer.objects.filter(user=request.user, question=q)
            else:
                q.answer = Answer.objects.none()
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
        statements = Statement.objects.filter(question=serializer.validated_data['question'])
        context = 'pass'
        run_statements(statements, context, self.request.user)
        
    def perform_update(self, serializer):
        serializer.save(user=self.request.user)
        statements = Statement.objects.filter(question=serializer.validated_data['question'])
        context = 'pass'
        delete_context(context)
        run_statements(statements, context, self.request.user)
