from django.contrib import admin
from django.urls import path, include

from rest_framework_jwt.views import obtain_jwt_token


urlpatterns = [
    path('core/', include('core.urls')),
    path('token-auth/', obtain_jwt_token),
    path('admin/', admin.site.urls),
]
