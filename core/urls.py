from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("classes/", views.classes, name="classes"),
    path("gallery/", views.gallery, name="gallery"),
    path("gallery/<slug:slug>/", views.gallery_category, name="gallery_category"),
    path("updates/", views.updates, name="updates"),
    path("contact/", views.contact, name="contact"),
]
