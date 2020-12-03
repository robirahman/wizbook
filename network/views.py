import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .models import User, Friendship, Message, Page, Post, Event, Event_Attendee, Group, Group_Member, Comment, Like


def index(request):
    return render(request, "network/index.html", {
        "posts": get_posts(request=request)
    })


def newsfeed(request):
    return render(request, "network/newsfeed.html", {
        "posts": get_posts(request=request, friend=request.user)
    })


def get_posts(request, profile=None, friend=None):
    posts = None
    if profile is not None:
        posts = Post.objects.filter(author=profile) # get all posts written by the user whose profile we are viewing
    elif friend is not None:
        posts = Post.objects.filter(author__friend1__friend2=friend) # get all posts written by the viewer's friends. need to also get author__friend2__friend1=friend
    else:
        posts = Post.objects.all() # if we're not looking at newsfeed or a profile, show all posts
    posts = posts.order_by("-timestamp").all()
    for post in posts:
        post.likes = Like.objects.filter(post=post).count() # count how many likes the post has
        post.comments = get_comments(post=post) # get all the comments on the post
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
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


def pages(request, id=None):
    if id is not None:
        return render(request, "network/pages.html", {"id": id})
    else:
        return render(request, "network/pages.html")


def groups(request, id=None):
    if id is not None:
        return render(request, "network/groups.html", {"id": id})
    else:
        return render(request, "network/groups.html")


def events(request, id=None):
    if id is not None:
        return render(request, "network/events.html", {"id": id})
    else:
        return render(request, "network/events.html")


@login_required
def profile(request, username):
    user = User.objects.filter(username=username)
    profile_data = user.values()[0]
    firstname = profile_data['first_name']
    lastname = profile_data['last_name']
    try:
        profile_pic = profile_data['profile_picture']
    except KeyError:
        profile_pic = None
    email = profile_data['email']
    posts = get_posts(request, profile=user[0])
    return render(request, "network/profile.html", {
        "username": username,
        "firstname": firstname,
        "lastname": lastname,
        "profile_pic": profile_pic,
        "email": email,
        "posts": posts
    })


@csrf_exempt
@login_required
def compose(request):

    # Composing a new email must be via POST
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

    # Get contents of email
    subject = data.get("subject", "")
    body = data.get("body", "")

    # Create one email for each recipient, plus sender
    users = set()
    users.add(request.user)
    users.update(recipients)
    for user in users:
        message = Message(
            user=user,
            sender=request.user,
            subject=subject,
            body=body,
            read=user == request.user
        )
        email.save()
        for recipient in recipients:
            email.recipients.add(recipient)
        email.save()

    return JsonResponse({"message": "Email sent successfully."}, status=201)


@login_required
def mailbox(request, mailbox):

    # Filter emails returned based on mailbox
    if mailbox == "inbox":
        emails = Email.objects.filter(
            user=request.user, recipients=request.user, archived=False
        )
    elif mailbox == "sent":
        emails = Email.objects.filter(
            user=request.user, sender=request.user
        )
    elif mailbox == "archive":
        emails = Email.objects.filter(
            user=request.user, recipients=request.user, archived=True
        )
    else:
        return JsonResponse({"error": "Invalid mailbox."}, status=400)

    # Return emails in reverse chronologial order
    emails = emails.order_by("-timestamp").all()
    return JsonResponse([email.serialize() for email in emails], safe=False)


@csrf_exempt
@login_required
def email(request, email_id):

    # Query for requested email
    try:
        email = Email.objects.get(user=request.user, pk=email_id)
    except Email.DoesNotExist:
        return JsonResponse({"error": "Email not found."}, status=404)

    # Return email contents
    if request.method == "GET":
        return JsonResponse(email.serialize())

    # Update whether email is read or should be archived
    elif request.method == "PUT":
        data = json.loads(request.body)
        if data.get("read") is not None:
            email.read = data["read"]
        if data.get("archived") is not None:
            email.archived = data["archived"]
        email.save()
        return HttpResponse(status=204)

    # Email must be via GET or PUT
    else:
        return JsonResponse({
            "error": "GET or PUT request required."
        }, status=400)


def messages(request):
    return render(request, "network/messages.html")

