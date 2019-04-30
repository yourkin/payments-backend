from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url

from rest_framework import routers
from rest_framework_jwt.views import obtain_jwt_token

from core.views import (TransactionViewSet, TransactionTypeViewSet)


router = routers.DefaultRouter()
router.register(r'transactions', TransactionViewSet)
router.register(r'transaction-types', TransactionTypeViewSet)


urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
    path('core/', include('core.urls')),
    path('token-auth/', obtain_jwt_token),
    path('admin/', admin.site.urls),
]
