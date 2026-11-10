from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("programmes/", views.programmes, name="programmes"),
    path("events/", views.events, name="events"),
    path("events/<slug:slug>/", views.event_detail, name="event_detail"),
    path("get-involved/", views.get_involved, name="get_involved"),
    path("contact/", views.contact, name="contact"),
]