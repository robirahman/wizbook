
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    path("pages", views.pages, name="pages"),
    path("pages/<int:id>", views.pages, name="page<int:id>"),
    path("groups", views.groups, name="groups"),
    path("groups/<int:id>", views.groups, name="group<int:id>"),
    path("events", views.events, name="events"),
    path("events/<int:id>", views.events, name="event<int:id>")
]
