from django.urls import include, path

urlpatterns = [
    path("", include("city_walks_app.urls")),
]
