from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.urls import reverse
from .models import User, Friendship, Message, Page, Post, Event, Event_Attendee, Group, Group_Member, Comment, Like


def get_posts(request, profile=None, friend=None):
    posts = None
    if profile is not None:
        # If we're looking at someone's profile, get their posts.
        posts = Post.objects.filter(author=profile)
    elif friend is not None:
        # If we're looking at our newsfeed, get posts by our friends.
        print("looking for friendships of: " + str(friend.username))
        friendships1 = Friendship.objects.filter(friend2=friend)
        friendships2 = Friendship.objects.filter(friend1=friend)
        print(friendships1 | friendships2)
        print("looking for friends of: " + str(friend.username))
        friends = [] # Initialize empty list of friends
        for friendship in friendships1:
            friends.append(friendship.friend1) # Add people who friended you to list
        for friendship in friendships2:
            friends.append(friendship.friend2) # Add people you friended to list
        print(friends)
        posts = Post.objects.none() # Initialize empty set of posts
        for author in friends:
            posts = posts | Post.objects.filter(author=author)
        print(posts)
    else:
        # If we're not looking at our newsfeed or someone's profile, show all posts.
        posts = Post.objects.all()
    posts = posts.order_by("-timestamp").all()
    for post in posts:
        post.numlikes = Like.objects.filter(post=post).count() # count how many likes the post has
        post.comments = get_comments(post=post) # get all the comments on the post
        post.numcomments = Comment.objects.filter(post=post).count() # count how many comments the post has
    try:
        page_num = request.GET.get('page', 1)
        posts = Paginator(posts, per_page=10).page(page_num)
    except PageNotAnInteger:
        posts = Paginator(posts, per_page=10).page(1)
    return posts


def get_comments(post=None, page=None, event=None, group=None):
    comments = None
    if post is not None:
        comments = Comment.objects.filter(post=post) # get comments on the specified post
    elif page is not None:
        comments = Comment.objects.filter(page=page) # get comments on the specified page
    elif event is not None:
        comments = Comment.objects.filter(event=event) # get comments on the specified event
    elif group is not None:
        comments = Comment.objects.filter(group=group) # get comments on the specified group
    return comments


def getPageEventGroup(request, view, page_id=None, event_id=None, group_id=None):
    id = page_id or event_id or group_id
    contents = None
    listing = None

    if page_id is not None:
        listing = Page.objects.get(id=id)
    elif event_id is not None:
        listing = Event.objects.get(id=id)
    elif group_id is not None:
        listing = Group.objects.get(id=id)
    elif view == "page":
        contents = Page.objects.all()
    elif view == "event":
        contents = Event.objects.all()
    elif view == "group":
        contents = Group.objects.all()
    
    return render(request, "network/page-event-group.html", {
        "view": view,
        "id": id,
        "listing": listing,
        "contents": contents
    })
    


def create(request, type):
    pass # need to implement page/event/group creation here

