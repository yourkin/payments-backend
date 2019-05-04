from django.urls import path

from .views import current_user, CreateUser


urlpatterns = [
    path('current_user/', current_user),
    path('users/', CreateUser.as_view()),
]
