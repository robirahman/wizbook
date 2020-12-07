from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from .models import (
    User, Friendship, Message,
    Event, Event_Attendee, Group, Group_Member,
    Post, Page, Comment, Like
    )


def get_posts(request, profile=None, friend=None):
    posts = None
    if profile is not None:  # Looking at someone's profile
        # get their posts
        posts = Post.objects.filter(author=profile)
    elif friend is not None:  # Looking at newsfeed
        # get posts by user's friends
        print("looking for friendships of: " + str(friend.username))
        friends = get_friends(request, friend)
        # Initialize empty set of posts
        posts = Post.objects.none()
        for author in friends:
            posts = posts | Post.objects.filter(author=author)
    else:  # Not looking at our newsfeed or someone's profile
        # show all posts
        posts = Post.objects.all()
    posts = posts.order_by("-timestamp").all()
    for post in posts:
        # count how many likes the post has
        post.numlikes = Like.objects.filter(post=post).count()
        # get all the comments on the post
        post.comments = get_comments(post=post)
        # count how many comments the post has
        post.numcomments = Comment.objects.filter(post=post).count()
    try:
        page_num = request.GET.get('page', 1)
        posts = Paginator(posts, per_page=10).page(page_num)
    except PageNotAnInteger:
        posts = Paginator(posts, per_page=10).page(1)
    return posts


def get_comments(post=None, page=None, event=None, group=None):
    comments = None
    if post is not None:
        # get comments on the specified post
        comments = Comment.objects.filter(post=post)
    elif page is not None:
        # get comments on the specified page
        comments = Comment.objects.filter(page=page)
    elif event is not None:
        # get comments on the specified event
        comments = Comment.objects.filter(event=event)
    elif group is not None:
        # get comments on the specified group
        comments = Comment.objects.filter(group=group)
    return comments


def get_friends(request, friend):
    friends = []  # Initialize empty list of friends
    friendships1 = Friendship.objects.filter(friend2=friend)
    friendships2 = Friendship.objects.filter(friend1=friend)
    for friendship in friendships1:
        # Add people who friended you to the list
        friends.append(friendship.friend1)
    for friendship in friendships2:
        # Add people you friended to the list
        friends.append(friendship.friend2)
    return friends


def get_peg(request, view, page_id=None, event_id=None, group_id=None):
    """ Gets a page, event, or group, depending on the type of id."""

    id = page_id or event_id or group_id
    contents = None
    listing = None
    fan = False
    attendee = False
    member = False
    fans = False
    attendees = False
    members = False

    if page_id is not None:
        page = Page.objects.get(pk=page_id)
        likes = Like.objects.filter(
            page=page,
            liker=request.user
            )
        if likes.count() == 0:
            fan = False
        else:
            fan = True
    if event_id is not None:
        event = Event.objects.get(pk=event_id)
        attendance = Event_Attendee.objects.filter(
            attendee=request.user,
            event=event
            )
        if attendance.count() == 0:
            attendee = False
        else:
            attendee = True
    if group_id is not None:
        group = Group.objects.get(pk=group_id)
        membership = Group_Member.objects.filter(
            member=request.user,
            group=group
            )
        if membership.count() == 0:
            member = False
        else:
            member = True

    if page_id is not None:
        listing = Page.objects.get(id=id)
        listing.comments = get_comments(page=listing)
        listing.numcomments = listing.comments.count()
        listing.people = User.objects.filter(likes_given__page=listing)
        if len(listing.people) != 0:
            fans = True
    elif event_id is not None:
        listing = Event.objects.get(id=id)
        listing.comments = get_comments(event=listing)
        listing.numcomments = listing.comments.count()
        listing.people = User.objects.filter(events_attended__event=listing)
        if len(listing.people) != 0:
            attendees = True
    elif group_id is not None:
        listing = Group.objects.get(id=id)
        listing.comments = get_comments(group=listing)
        listing.numcomments = listing.comments.count()
        listing.people = User.objects.filter(groups_joined__group=listing)
        if len(listing.people) != 0:
            members = True
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
        "contents": contents,
        "fan": fan,
        "attendee": attendee,
        "member": member,
        "fans": fans,
        "attendees": attendees,
        "members": members
    })


def create(request):
    if request.method == "POST":
        peg_type = request.POST["peg-type"]
        owner = request.user
        name = request.POST["name"]
        picture = request.POST["picture"]
        description = request.POST["description"]
        if peg_type == "page":
            page = Page.objects.create(
                owner=owner,
                name=name,
                picture=picture,
                description=description
                )
            page.save()
            id = Page.objects.filter(name=name)[0].id
            return get_peg(request, view="page", page_id=id)
        elif peg_type == "event":
            date = request.POST["date"]
            place = request.POST["location"]
            event = Event.objects.create(
                owner=owner,
                name=name,
                picture=picture,
                description=description,
                date=date,
                place=place
                )
            event.save()
            id = Event.objects.filter(name=name)[0].id
            return get_peg(request, view="event", event_id=id)
        elif peg_type == "group":
            group = Group.objects.create(
                owner=owner,
                name=name,
                picture=picture,
                description=description
                )
            group.save()
            id = Group.objects.filter(name=name)[0].id
            return get_peg(request, view="group", group_id=id)
    else:
        return HttpResponseRedirect(reverse("index"))
