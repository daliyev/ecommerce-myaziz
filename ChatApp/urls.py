from django.urls import path
from .views import SendMessageApi
urlpatterns = [
    path('', SendMessageApi.as_view()),
]