from questionnaire.models import *
from questionnaire.serializers import *
from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework import permissions
from questionnaire.rdf import get_definitions, delete_context, run_statements
from rest_framework import exceptions


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

class SurveyList(viewsets.ReadOnlyModelViewSet):
    serializer_class = SurveySerializer
    authentication_classes = (TokenAuthentication,)

    def list(self, request):
        if request.user.is_authenticated():
            if 'survey' in request.session:
                try:
                    survey = Survey.objects.get(pk=request.session['survey'])
                    serializer = self.get_serializer(survey)
                    return Response(serializer.data)
                except:
                    return Response()
        return Response()

class ChebiList(viewsets.ReadOnlyModelViewSet):
    queryset = Chebi.objects.all()
    serializer_class = ChebiSerializer

    def list(self, request, partial):
        drugs = Chebi.objects.filter(name__contains=partial)[:10]
        return Response(self.get_serializer(drugs, many=True).data)


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
        
class SurveyViewSet(viewsets.ModelViewSet):
    serializer_class = SurveySerializer
    queryset = Survey.objects.all()
    permission_classes = (AnswerAccessPermission,)
    authentication_classes = (TokenAuthentication,)
    lookup_fields = ('user')

    def perform_create(self, serializer):
        if 'survey' not in self.request.session:
            raise exceptions.APIException(detail="No session exists")
        else:
            survey = Survey.objects.get(pk=self.request.session['survey'])
            survey.name = serializer.validated_data['name']
            survey.save()

class AnswerViewSet(viewsets.ModelViewSet):
    serializer_class = AnswerSerializer
    queryset = Answer.objects.all()
    permission_classes = (AnswerAccessPermission,)
    authentication_classes = (TokenAuthentication,)
    lookup_fields = ('question', 'user')

    def perform_create(self, serializer):
        if 'survey' not in self.request.session:
            raise exceptions.APIException(detail="No session exists")
            return
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

class NewSurveyView(APIView):
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        if request.user.is_authenticated():
            s = Survey(user=request.user)
            s.save()
            request.session['survey'] = s.id
            print("New Survey")
            return Response(True)
        return Response("User not authenticated\n{}".format(request.user.is_authenticated()))

class ChangeSurveyView(APIView):
    authentication_classes = (TokenAuthentication,)

    def delete(self, request, survey_id):
        if request.user.is_authenticated():
            s = Survey.objects.get(pk=survey_id) 
            if(s):
                if s.id == request.session['survey']:
                    request.session['survey'] = None
                    s.delete()
                    new_survey = Survey.objects.first()
                    if new_survey:
                        request.session['survey'] = new_survey.id
                else:
                    s.delete()
                return Response(True)
            else:
                return Response("Survey {} not found".format(survey_id))
        return Response("User not authenticated\n{}".format(request.user.is_authenticated()))

    def get(self, request, survey_id):
        if request.user.is_authenticated():
            s = Survey.objects.get(pk=survey_id) 
            if(s):
                request.session['survey'] = s.id
                return Response(True)
            else:
                return Response("Survey {} not found".format(survey_id))
        return Response("User not authenticated\n{}".format(request.user.is_authenticated()))
