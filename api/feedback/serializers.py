from rest_framework import serializers
from api.models import *
class QuestionSerializer(serializers.Serializer):
    title=serializers.CharField(required=True,max_length=50)
    question=serializers.CharField(required=True,max_length=500)
