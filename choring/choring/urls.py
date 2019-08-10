from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('chores/', include('chores.urls')),
    path(r'^admin/', admin.site.urls),
]
