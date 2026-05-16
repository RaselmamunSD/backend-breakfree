from rest_framework import serializers
from .models import ChatSession, ChatMessage, FearForecastRecord

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'role', 'content', 'created_at']

class ChatSessionSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True)
    class Meta:
        model = ChatSession
        fields = ['id', 'user', 'created_at', 'updated_at', 'messages']
        read_only_fields = ['user']

class FearForecastRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = FearForecastRecord
        fields = ['id', 'user', 'fear', 'belief_strength', 'ai_prediction', 'outcome', 'ai_insight', 'created_at', 'updated_at']
        read_only_fields = ['user', 'ai_prediction', 'ai_insight']

