from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url

from rest_framework import routers
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework_swagger.views import get_swagger_view

from core.views import (TransactionViewSet, TransactionTypeViewSet,
                        AccountViewSet, UserViewSet)


router = routers.DefaultRouter()
router.register(r'transactions', TransactionViewSet)
router.register(r'transaction-types', TransactionTypeViewSet)
router.register(r'accounts', AccountViewSet)
router.register(r'users', UserViewSet)


# API Live Documentation
schema_view = get_swagger_view(title='Payments API')


urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
    url(r'^dev/$', schema_view),
    path('core/', include('core.urls')),
    path('token-auth/', obtain_jwt_token),
    path('admin/', admin.site.urls),
]
