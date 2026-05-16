from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChatSessionViewSet, FearForecastViewSet

router = DefaultRouter()
router.register(r'chat', ChatSessionViewSet, basename='chat')
router.register(r'fear-forecast', FearForecastViewSet, basename='fear-forecast')

urlpatterns = [
    path('', include(router.urls)),
]

