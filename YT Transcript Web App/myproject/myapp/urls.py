from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/languages', views.get_languages, name='get_languages'),
    path('api/transcript', views.get_transcript, name='get_transcript'),
    path('api/text/whisper', views.get_video_text_whisper, name='get_video_text_whisper'),
]
