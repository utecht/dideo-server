from questionnaire.models import *
from rest_framework.serializers import ModelSerializer

class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')

class QuestionSerializer(ModelSerializer):
    class Meta:
        model = Question
        fields = ('id', 'text', 'q_type', 'options')
        depth = 1
