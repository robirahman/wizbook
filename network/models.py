from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    profile_picture = models.TextField(blank=True) # Need to add a field to registration form that takes this as input.
    birthday = models.DateField(blank=True, auto_now_add=False) # Need to ask this upon registration.
    
    def __str__(self):
        return "User: " + str(self.username)


class Friendship(models.Model):
    friend1 = models.ForeignKey("User", on_delete=models.CASCADE, related_name="friended_by")
    friend2 = models.ForeignKey("User", on_delete=models.CASCADE, related_name="people_friended")
    
    def __str__(self):
        return str(self.friend1) + " friended " + str(self.friend2)


class Message(models.Model):
    sender = models.ForeignKey("User", on_delete=models.CASCADE, related_name="sender")
    recipient = models.ForeignKey("User", on_delete=models.CASCADE, related_name="recipient")
    body = models.TextField(blank=True)

    def __str__(self):
        return str(self.sender) + " wrote to " + str(self.recipient) + ": " + str(self.body)[:30]



class Page(models.Model):
    owner = models.ForeignKey("User", on_delete=models.CASCADE, related_name="pages_owned")
    name = models.CharField(unique=True, max_length=50)
    picture = models.TextField(blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return "Page: " + str(self.name)


class Post(models.Model):
    author = models.ForeignKey("User", on_delete=models.CASCADE, related_name="posts_written")
    timestamp = models.DateTimeField(auto_now_add=True)
    body = models.TextField(blank=True)

    def __str__(self):
        return str(self.author) + " wrote: " + str(self.body)[:30]

class Event(models.Model):
    name = models.CharField(unique=True, max_length=50)
    date = models.DateTimeField(auto_now_add=False)
    place = models.TextField(blank=True)
    description = models.TextField(blank=True)
    picture = models.TextField(blank=True)

    def __str__(self):
        return "Event: " + str(self.name)


class Event_Attendee(models.Model):
    attendee = models.ForeignKey("User", on_delete=models.CASCADE, related_name="events_attended")
    event = models.ForeignKey("Event", on_delete=models.CASCADE, related_name="attendees")

    def __str__(self):
        return str(self.attendee) + " attends " + str(self.event)


class Group(models.Model):
    name = models.CharField(unique=True, max_length=50)
    description = models.TextField(blank=True)
    picture = models.TextField(blank=True)

    def __str__(self):
        return "Group: " + str(self.name)


class Group_Member(models.Model):
    member = models.ForeignKey("User", on_delete=models.CASCADE, related_name="groups_joined")
    group = models.ForeignKey("Group", on_delete=models.CASCADE, related_name="members")

    def __str__(self):
        return str(self.member) + " is a member of group " + str(self.group)


class Comment(models.Model):
    author = models.ForeignKey("User", on_delete=models.CASCADE, related_name="comments_written")
    page = models.ForeignKey("Page", on_delete=models.CASCADE, related_name="page_comments")
    post = models.ForeignKey("Post", on_delete=models.CASCADE, related_name="post_comments")
    event = models.ForeignKey("Event", on_delete=models.CASCADE, related_name="event_comments")
    group = models.ForeignKey("Group", on_delete=models.CASCADE, related_name="group_comments")

    def __str__(self):
        return str(self.author) + " wrote a comment." # need to get text of comment


class Like(models.Model):
    liker = models.ForeignKey("User", on_delete=models.CASCADE, related_name="likes_given")
    page = models.ForeignKey("Page", on_delete=models.CASCADE, related_name="page_likes")
    post = models.ForeignKey("Post", on_delete=models.CASCADE, related_name="post_likes")
    comment = models.ForeignKey("Comment", on_delete=models.CASCADE, related_name="comment_likes")

    def __str__(self):
        return str(self.liker) + " liked something." # need to get name or contents of liked object

