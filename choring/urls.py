"""choring URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from django.views.generic import TemplateView
from choring.chores import views as chores_views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from accounts.api import RegisterAPIView, ProfileAPIView

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='base.html'), name='home'),
    path('', include(router.urls)),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    # API endpoints
    path('api/accounts/register/', RegisterAPIView.as_view(), name='api-register'),
    path('api/accounts/profile/', ProfileAPIView.as_view(), name='api-profile'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/chores/week/', chores_views.chores_for_week, name='api-chores-week'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]

# Serve SPA
urlpatterns += [
    path('app/', TemplateView.as_view(template_name='frontend/index.html'), name='app'),
]
