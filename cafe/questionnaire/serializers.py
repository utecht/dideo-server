from questionnaire.models import *
from rest_framework import serializers

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('id', 'text', 'q_type', 'options', 'answer', 'tags', 'help_text', 'depends_on')
        depth = 1

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ('text', 'check', 'integer', 'yesno', 'question')

class DefinitionSerializer(serializers.Serializer):
    word = serializers.CharField(max_length=200)
    definition = serializers.CharField(max_length=2000)
