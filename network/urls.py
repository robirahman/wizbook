
from django.urls import path

from . import views, utils

urlpatterns = [

    # Log in, log out, and sign up
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    # Home page and news feed
    path("", views.index, name="index"),
    path("newsfeed", views.newsfeed, name="newsfeed"),

    # Write a post
    path("post", views.write, name="write_post"),
    # Like a post
    path("post/<int:post_id>/like", views.like, name="like_post"),
    # Edit a post
    path("post/<int:post_id>/edit", views.edit, name="edit_post"),
    # Comment on a post
    path("post/<int:post_id>/comment", views.comment, name="comment_on_post"),

    # View user profiles
    path("users/<str:username>", views.profile, name="view_profile"),
    # See user's friend list
    path("users/<str:username>", views.friends_list, name="friends_list"),
    # Add/remove friendship
    path("users/<str:username>/add", views.add_friend, name="add_friend"),

    # Messaging: view inbox/sent/archive
    path("messages", views.messages, name="messages"),
    # Messaging: API routes
    path("compose", views.compose, name="compose"),
    path("messages/<int:email_id>", views.email, name="email"),
    path("messages/<str:mailbox>", views.mailbox, name="mailbox"),

    # Pages, events, groups: view
    path("pages", views.pages, name="pages"),
    path("pages/<int:id>", views.pages, name="view_page"),
    path("groups", views.groups, name="groups"),
    path("groups/<int:id>", views.groups, name="view_group"),
    path("events", views.events, name="events"),
    path("events/<int:id>", views.events, name="view_event"),
    # Pages, events, groups: create new
    path("create", utils.create, name="create"),
    # Pages, events, groups: add comment
    path("page/<int:page_id>/comment", views.comment, name="comment_on_page"),
    path("event/<int:event_id>/comment", views.comment, name="comment_on_event"),
    path("group/<int:group_id>/comment", views.comment, name="comment_on_group"),

]
