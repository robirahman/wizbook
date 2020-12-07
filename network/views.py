import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .models import (
    User, Friendship, Message,
    Event, Event_Attendee, Group, Group_Member,
    Post, Page, Comment, Like
    )
from .utils import get_posts, get_comments, get_friends, get_peg


def index(request):
    return render(request, "network/index.html", {
        "posts": get_posts(request=request)
    })


def newsfeed(request):
    return render(request, "network/index.html", {
        "posts": get_posts(request=request, friend=request.user)
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        birthday = request.POST["birthday"]
        profile_picture = request.POST["profile_picture"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            print(profile_picture)
            user.first_name = first_name
            user.last_name = last_name
            user.birthday = birthday
            user.profile_picture = profile_picture
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


@csrf_exempt  # replace with csrf token
def profile(request, username):
    user = User.objects.filter(username=username)
    profile_data = user.values()[0]
    firstname = profile_data['first_name']
    lastname = profile_data['last_name']
    try:
        profile_pic = profile_data['profile_picture']
    except KeyError:
        profile_pic = None
    try:
        birthday = profile_data['birthday']
    except KeyError:
        birthday = None
    email = profile_data['email']
    posts = get_posts(request, profile=user[0])
    friend = request.user in get_friends(request, user.values()[0]["id"])
    friends = get_friends(request, user[0])
    return render(request, "network/profile.html", {
        "username": username,
        "firstname": firstname,
        "lastname": lastname,
        "birthday": birthday,
        "profile_pic": profile_pic,
        "email": email,
        "friend": friend,
        "friends": friends,
        "posts": posts
    })


@csrf_exempt
@login_required
def compose(request):

    # Composing a new message must be via POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    # Check recipient emails
    data = json.loads(request.body)
    emails = [email.strip() for email in data.get("recipients").split(",")]
    if emails == [""]:
        return JsonResponse({
            "error": "At least one recipient required."
        }, status=400)

    # Convert email addresses to users
    recipients = []
    for email in emails:
        try:
            user = User.objects.get(email=email)
            recipients.append(user)
        except User.DoesNotExist:
            return JsonResponse({
                "error": f"User with email {email} does not exist."
            }, status=400)

    # Get contents of message
    subject = data.get("subject", "")
    body = data.get("body", "")

    # Create one message for each recipient, plus sender
    users = set()
    users.add(request.user)
    users.update(recipients)
    for user in users:
        message = Message(
            owner=user,
            sender=request.user,
            subject=subject,
            body=body,
            read=user == request.user
        )
        message.save()
        for recipient in recipients:
            message.recipients.add(recipient)
        message.save()

    return JsonResponse({"message": "Message sent successfully."}, status=201)


@csrf_exempt  # replace with csrf token
@login_required
def mailbox(request, mailbox):

    # Filter messages returned based on mailbox
    if mailbox == "inbox":
        messages = Message.objects.filter(
            owner=request.user, recipients=request.user, archived=False
        )
    elif mailbox == "sent":
        messages = Message.objects.filter(
            owner=request.user, sender=request.user
        )
    elif mailbox == "archive":
        messages = Message.objects.filter(
            owner=request.user, recipients=request.user, archived=True
        )
    else:
        return JsonResponse({"error": "Invalid mailbox."}, status=400)

    # Return messages in reverse chronologial order
    messages = messages.order_by("-timestamp").all()
    return JsonResponse(
        [message.serialize() for message in messages],
        safe=False
        )


@csrf_exempt
@login_required
def email(request, email_id):

    # Query for requested message
    try:
        message = Message.objects.get(owner=request.user, pk=email_id)
    except Message.DoesNotExist:
        return JsonResponse({"error": "Message not found."}, status=404)

    # Return message contents
    if request.method == "GET":
        return JsonResponse(message.serialize())

    # Update whether message is read or should be archived
    elif request.method == "PUT":
        data = json.loads(request.body)
        if data.get("read") is not None:
            message.read = data["read"]
        if data.get("archived") is not None:
            message.archived = data["archived"]
        message.save()
        return HttpResponse(status=204)

    # Message must be via GET or PUT
    else:
        return JsonResponse({
            "error": "GET or PUT request required."
        }, status=400)


@csrf_exempt  # replace with csrf token
@login_required
def messages(request):
    return render(request, "network/messages.html")


def pages(request, id=None):
    return get_peg(request=request, view="page", page_id=id)


def events(request, id=None):
    return get_peg(request=request, view="event", event_id=id)


def groups(request, id=None):
    return get_peg(request=request, view="group", group_id=id)


@csrf_exempt
@login_required
def write(request):

    # Composing a new croak must be via POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    # Get contents of post
    data = json.loads(request.body)
    body = data.get("body", "")

    # Create post
    post = Post(
        author=request.user,
        body=body
    )
    post.save()

    return JsonResponse({"message": "Post saved successfully."}, status=201)


@csrf_exempt
@login_required
def edit(request, post_id):
    # Editing a tweet must be via POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    # Get contents of form
    data = json.loads(request.body)
    body = data.get("body", "")
    # post_id = data.get("id", "")

    # Query for post
    post = Post.objects.get(id=post_id)

    # Check if logged in user is author
    is_author = request.user == post.author

    if is_author:
        # Save edit to post
        post.body = body
        post.save()
        return JsonResponse({
            "message": "Post edited successfully."
            }, status=201)
    else:
        # Block the edit
        return JsonResponse({
            "message": "You cannot edit that post."
            })


@csrf_exempt
@login_required
def comment(request, post_id=None, page_id=None, event_id=None, group_id=None):
    # Writing a comment must be via POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    # Get contents of form
    data = json.loads(request.body)
    text = data.get("text", "")

    # If user is commenting on a post
    if post_id is not None:
        post = Post.objects.filter(id=post_id)[0]
        comment = Comment.objects.create(
            body=text,
            author=request.user,
            post=post
            )
    # If user is commenting on a page
    elif page_id is not None:
        page = Page.objects.filter(id=page_id)[0]
        comment = Comment.objects.create(
            body=text,
            author=request.user,
            page=page
            )
    # If user is commenting on an event
    elif event_id is not None:
        event = Event.objects.filter(id=event_id)[0]
        comment = Comment.objects.create(
            body=text,
            author=request.user,
            event=event
            )
    # If user is commenting on a group
    elif group_id is not None:
        group = Group.objects.filter(id=group_id)[0]
        comment = Comment.objects.create(
            body=text,
            author=request.user,
            group=group
            )

    # Save comment to database
    comment.save()

    return JsonResponse({"message": "Comment posted successfully."})


@login_required
def like(request, post_id):
    # Query for requested post
    try:
        target = Post.objects.get(id=post_id)
        print(target)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)

    # Delete an existing like. If there isn't one, add a like.
    try:
        old_like = Like.objects.get(post=target, liker=request.user)
        old_like.delete()
        result = "unliked"
    except Like.DoesNotExist:
        new_like = Like(post=target, liker=request.user)
        new_like.save()
        result = "liked"
    new_likes = Like.objects.filter(post=target).count()
    return JsonResponse({"result": result, "newLikes": new_likes}, status=200)


@login_required
def friends_list(request, username):
    pass


@csrf_exempt
@login_required
def add_friend(request, username):
    """ Toggles friendship with the target user. """
    # query for the person we are viewing
    person = User.objects.filter(username=username)[0]
    # get all of the current user's friends
    friends = get_friends(request, person)
    if request.user in friends:
        set1 = Friendship.objects.filter(friend1=request.user, friend2=person)
        set2 = Friendship.objects.filter(friend1=person, friend2=request.user)
        friendship = set1 | set2
        friendship.delete()
        friend = False
    else:
        friendship = Friendship.objects.create(
            friend1=request.user,
            friend2=person
            )
        friendship.save()
        friend = True
    return HttpResponseRedirect(reverse("view_profile", kwargs={
        "username": person.username
        })
        )


@csrf_exempt
@login_required
def like_attend_join(request, page_id=None, event_id=None, group_id=None):
    """ Like page, attend event, or join group """
    # query for the person we are viewing
    person = request.user
    if page_id is not None:
        page = Page.objects.get(pk=page_id)
        likes = Like.objects.filter(page=page, liker=person).count()
        if likes == 0:
            like = Like.objects.create(page=page, liker=person)
            like.save()
            fan = True
        else:
            like = Like.objects.get(page=page, liker=person)
            like.delete()
            fan = False
        return HttpResponseRedirect(reverse(
            "view_page",
            kwargs={"id": page_id}
            ))
    if event_id is not None:
        event = Event.objects.get(pk=event_id)
        attendance = Event_Attendee.objects.filter(
            attendee=person,
            event=event
            )
        if attendance.count() == 0:
            event_attendee = Event_Attendee.objects.create(
                attendee=person,
                event=event
                )
            event_attendee.save()
            attendee = True
        else:
            event_attendee = Event_Attendee.objects.get(
                attendee=person,
                event=event
                )
            event_attendee.delete()
            attendee = False
        return HttpResponseRedirect(reverse(
            "view_event",
            kwargs={"id": event_id}
            ))
    if group_id is not None:
        group = Group.objects.get(pk=group_id)
        membership = Group_Member.objects.filter(
            member=person,
            group=group
            )
        if membership.count() == 0:
            group_member = Group_Member.objects.create(
                member=person,
                group=group
                )
            group_member.save()
            member = True
        else:
            group_member = Group_Member.objects.get(
                member=person,
                group=group
                )
            group_member.delete()
            member = False
        return HttpResponseRedirect(reverse(
            "view_group",
            kwargs={"id": group_id}
            ))
