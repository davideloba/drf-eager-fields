from django.urls import include, path
from django.urls import include
from django.contrib import admin
from django.contrib.admindocs import urls as admindocs_urls
from app import urls as app_urls

urlpatterns = [
    # django-admin:
    path('admin/', admin.site.urls),

    path("api/app/", include(app_urls)),
]
