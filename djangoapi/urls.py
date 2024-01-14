from django.urls import path
from .api.Subtitle import Subtitle
from .api.Subtitle import Translate
from .api.checkgrammar import CheckGRM
from .api.summarize import Summary

urlpatterns = [
    path('subtitles/', Subtitle.as_view(), name='get_subtitle'),
    path('translateVtt/', Translate.as_view(), name='translate'),
    path('checkgrm/', CheckGRM.as_view(), name='getCheckgrm'),
    path('summarize/', Summary.as_view(), name='getSummary'),
]
