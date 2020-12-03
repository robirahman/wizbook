from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import User, Friendship, Message, Page, Post, Event, Event_Attendee, Group, Group_Member, Comment, Like


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


