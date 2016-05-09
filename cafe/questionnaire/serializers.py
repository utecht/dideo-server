from questionnaire.models import *
from rest_framework import serializers
from django.contrib.auth.models import User

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ('text', 'check', 'integer', 'yesno', 'question')

class UserAnswer(serializers.ModelSerializer):
    # user request to find specific user
    pass

class DefinitionSerializer(serializers.Serializer):
    word = serializers.CharField(max_length=200)
    definition = serializers.CharField(max_length=2000)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'is_staff', 'email')

class QuestionSerializer(serializers.ModelSerializer):
    disabled = serializers.SerializerMethodField('is_disabled')
    graph = serializers.SerializerMethodField('has_graph')
    depends_on = serializers.SerializerMethodField('get_depends')

    def is_disabled(self, question):
        user = self.context['request'].user
        return question.disabled(user)

    def has_graph(self, question):
        s = Statement.objects.filter(question=question)
        return bool(s)

    def get_depends(self, question):
        deps = []
        for d in question.depends_on.all():
            deps.append(d.id)
        return deps

    class Meta:
        model = Question
        fields = ('id', 'text', 'q_type', 'options', 'answer', 'tags', 'help_text', 'disabled', 'graph', 'depends_on')
        depth = 1
