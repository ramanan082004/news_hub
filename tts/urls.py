from django.urls import path
from . import views

urlpatterns = [
    path('generate/', views.generate_tts, name='generate_tts'),
]