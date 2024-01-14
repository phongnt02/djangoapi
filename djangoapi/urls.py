from django.urls import path
from .api.Subtitle import Subtitle
from .api.Subtitle import Translate

urlpatterns = [
    path('subtitles/', Subtitle.as_view(), name='get_subtitle'),
    path('translateVtt/', Translate.as_view(), name='translate'),
]
