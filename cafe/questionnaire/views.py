from questionnaire.models import *
from questionnaire.serializers import *
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
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
    queryset = Category.objects.all().order_by('order')
    serializer_class = CategorySerializer
    
class QuestionList(viewsets.ReadOnlyModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    authentication_classes = (TokenAuthentication,)

    def list(self, request, category):
        print(request.user)
        if request.user.is_authenticated():
            if 'survey' not in request.session:
                s = Survey(user=request.user)
                s.save()
                request.session['survey'] = s.id
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
        
class UserView(viewsets.ViewSet):
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        if request.user:
            serializer = UserSerializer(request.user)
            return Response(serializer.data)
        else:
            return Response()

    def list(self, request):
        if request.user:
            serializer = UserSerializer(request.user)
            return Response(serializer.data)
        else:
            return Response()

class AnswerViewSet(viewsets.ModelViewSet):
    serializer_class = AnswerSerializer
    queryset = Answer.objects.all()
    permission_classes = (AnswerAccessPermission,)
    authentication_classes = (TokenAuthentication,)
    lookup_fields = ('question', 'user')

    def perform_create(self, serializer):
        survey = Survey.objects.get(id=self.request.session['survey'])
        Answer.objects.filter(survey=survey, question=serializer.validated_data['question']).delete()
        serializer.save(survey=survey)
        statements = Statement.objects.filter(question=serializer.validated_data['question'])
        context = 'pass'
        run_statements(statements, context, self.request.user)
        
    def perform_update(self, serializer):
        serializer.save(user=self.request.user)
        statements = Statement.objects.filter(question=serializer.validated_data['question'])
        context = 'pass'
        delete_context(context)
        run_statements(statements, context, self.request.user)

@csrf_exempt
def new_survey(request):
    if request.user.is_authenticated():
        s = Survey(user=request.user)
        s.save()
        request.session['survey'] = s.id
        print("New Survey")
        return HttpResponse(True)
    return HttpResponse(False)
