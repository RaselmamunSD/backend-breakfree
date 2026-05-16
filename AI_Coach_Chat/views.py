from rest_framework import viewsets, status, views
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import ChatSession, ChatMessage, FearForecastRecord
from .serializers import ChatSessionSerializer, ChatMessageSerializer, FearForecastRecordSerializer
from .chat import AICoach
from .predict import FearForecast
from .prompts import SYSTEM_PROMPT_CHAT

class ChatSessionViewSet(viewsets.ModelViewSet):
    serializer_class = ChatSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def message(self, request, pk=None):
        session = self.get_object()
        user_message_content = request.data.get('message')
        if not user_message_content:
            return Response({'error': 'Message content is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Save user message
        ChatMessage.objects.create(session=session, role='user', content=user_message_content)

        # Build history for OpenAI
        messages = list(session.messages.order_by('created_at'))
        history = [{'role': 'system', 'content': SYSTEM_PROMPT_CHAT}]
        for msg in messages:
            history.append({'role': msg.role, 'content': msg.content})

        # Call AI
        coach = AICoach()
        try:
            ai_reply = coach.get_reply(history)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Save AI reply
        ai_message = ChatMessage.objects.create(session=session, role='assistant', content=ai_reply)

        return Response({
            'user_message': user_message_content,
            'ai_reply': ChatMessageSerializer(ai_message).data
        })

class FearForecastViewSet(viewsets.ModelViewSet):
    serializer_class = FearForecastRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FearForecastRecord.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        record = serializer.save(user=self.request.user)
        forecast = FearForecast()
        try:
            result = forecast.generate_forecast(record.fear, record.belief_strength)
            record.ai_prediction = result['ai_response']
            record.save()
        except Exception as e:
            # Handle or log error
            pass

    @action(detail=True, methods=['post'])
    def log_outcome(self, request, pk=None):
        record = self.get_object()
        outcome = request.data.get('outcome')
        if not outcome:
            return Response({'error': 'Outcome is required'}, status=status.HTTP_400_BAD_REQUEST)

        forecast = FearForecast()
        try:
            result = forecast.generate_insight(record.fear, record.ai_prediction, outcome)
            record.outcome = outcome
            record.ai_insight = result['insight']
            record.save()
            return Response(FearForecastRecordSerializer(record).data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

