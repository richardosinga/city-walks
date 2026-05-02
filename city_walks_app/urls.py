from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="walks_home"),
    path("content-image/<path:path>", views.content_image, name="content_image"),
    path("<path:path>.gpx", views.walk_gpx, name="walk_gpx"),
    path("<path:path>", views.walk_detail, name="walk_detail"),
]
