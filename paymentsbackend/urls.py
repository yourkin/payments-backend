from django.contrib import admin
from django.urls import path, include, re_path

from rest_framework import routers
from rest_framework_jwt.views import obtain_jwt_token

from core.views import (TransactionViewSet, TransactionTypeViewSet,
                        AccountViewSet, UserViewSet, index)


router = routers.DefaultRouter()
router.register(r'transactions', TransactionViewSet)
router.register(r'transaction-types', TransactionTypeViewSet)
router.register(r'accounts', AccountViewSet)
router.register(r'users', UserViewSet)


urlpatterns = [
    path('', index, name='index'),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls',
                              namespace='rest_framework')),
    path('core/', include('core.urls')),
    path('token-auth/', obtain_jwt_token),
    path('admin/', admin.site.urls),
    re_path(r'^(?:.*)/?$', index),
]
