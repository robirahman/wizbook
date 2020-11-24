from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    profile_picture = models.TextField() # Need to add a field to registration form that takes this as input.
    birthday = models.DateField(auto_now_add=False) # Need to ask this upon registration.


class Friendship(models.Model):
    friend1 = models.ForeignKey("User", on_delete=models.CASCADE, related_name="friended_by")
    friend2 = models.ForeignKey("User", on_delete=models.CASCADE, related_name="people_friended")


class Message(models.Model):
    sender = models.ForeignKey("User", on_delete=models.CASCADE, related_name="sender")
    recipient = models.ForeignKey("User", on_delete=models.CASCADE, related_name="recipient")
    body = models.TextField(blank=True)


class Page(models.Model):
    owner = models.ForeignKey("User", on_delete=models.CASCADE, related_name="pages_owned")
    name = models.CharField(unique=True, max_length=50)
    picture = models.TextField(blank=True)
    description = models.TextField(blank=True)


class Post(models.Model):
    author = models.ForeignKey("User", on_delete=models.CASCADE, related_name="posts_written")
    timestamp = models.DateTimeField(auto_now_add=True)
    body = models.TextField(blank=True)

class Event(models.Model):
    name = models.CharField(unique=True, max_length=50)
    date = models.DateTimeField(auto_now_add=False)
    place = models.TextField(blank=True)
    description = models.TextField(blank=True)
    picture = models.TextField(blank=True)


class Event_Attendee(models.Model):
    attendee = models.ForeignKey("User", on_delete=models.CASCADE, related_name="events_attended")
    event = models.ForeignKey("Event", on_delete=models.CASCADE, related_name="attendees")


class Group(models.Model):
    name = models.CharField(unique=True, max_length=50)
    description = models.TextField(blank=True)
    picture = models.TextField(blank=True)


class Group_Member(models.Model):
    member = models.ForeignKey("User", on_delete=models.CASCADE, related_name="groups_joined")
    group = models.ForeignKey("Group", on_delete=models.CASCADE, related_name="members")


class Comment(models.Model):
    author = models.ForeignKey("User", on_delete=models.CASCADE, related_name="comments_written")
    page = models.ForeignKey("Page", on_delete=models.CASCADE, related_name="page_comments")
    post = models.ForeignKey("Post", on_delete=models.CASCADE, related_name="post_comments")
    event = models.ForeignKey("Event", on_delete=models.CASCADE, related_name="event_comments")
    group = models.ForeignKey("Group", on_delete=models.CASCADE, related_name="group_comments")


class Like(models.Model):
    liker = models.ForeignKey("User", on_delete=models.CASCADE, related_name="likes_given")
    page = models.ForeignKey("Page", on_delete=models.CASCADE, related_name="page_likes")
    post = models.ForeignKey("Post", on_delete=models.CASCADE, related_name="post_likes")
    comment = models.ForeignKey("Comment", on_delete=models.CASCADE, related_name="comment_likes")

