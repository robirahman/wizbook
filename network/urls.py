
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    path("pages", views.pages, name="pages"),
    path("pages/<int:id>", views.pages, name="view_page"),
    path("groups", views.groups, name="groups"),
    path("groups/<int:id>", views.groups, name="view_group"),
    path("events", views.events, name="events"),
    path("events/<int:id>", views.events, name="view_event"),

    path("users/<str:username>", views.profile, name="view_profile"),

    path("messages", views.messages, name="messages"),



    # messaging API Routes
    path("emails", views.compose, name="compose"),
    path("emails/<int:email_id>", views.email, name="email"),
    path("emails/<str:mailbox>", views.mailbox, name="mailbox"),
]
