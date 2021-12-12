from django.urls import include, path
from app import urls as app_urls

urlpatterns = [
    path("api/app/", include(app_urls)),
]
