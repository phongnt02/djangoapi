# myapp/urls.py

from django.urls import path
from .api.Subtitle import Subtitle

urlpatterns = [
    path('subtitles/', Subtitle.as_view(), name='getSubtitle'),
]
