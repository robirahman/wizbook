from django.contrib import admin
from .models import User, Friendship, Message, Page, Post, Event, Event_Attendee, Group, Group_Member, Comment, Like

# Register your models here.
admin.site.register(User)
admin.site.register(Friendship)
admin.site.register(Message)
admin.site.register(Page)
admin.site.register(Post)
admin.site.register(Event)
admin.site.register(Event_Attendee)
admin.site.register(Group)
admin.site.register(Group_Member)
admin.site.register(Comment)
admin.site.register(Like)
