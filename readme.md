Project description:
This is Wizbook, a magical equivalent to the Muggle website known as Facebook.
You can register a user profile and specify your birthday and a (URL of a) profile image.
You can write text posts on the site. You can edit your own posts and like posts written by other users. You can comment on posts.
You can create Pages, Events, and Groups, which people can like, attend, or join.
You can send messages to other users by entering the email addresses they signed up with.
You can add other users as friends, which includes their posts in your personal newsfeed. (The public timeline shows everyone's posts.)

There are four main Django HTML templates for this application:
    index.html shows all posts or posts from your friends, depending on the route.
    messages.html shows an online messaging mailbox similar to the previous email application.
    page-event-group.html lists all the pages, events, or groups, or shows a specific one.
    profile.html shows the profile of a specified user.
The layout.html, login.html, and register.html files have similar functions as in past projects.

models.py specifies the different databases for this project, such as users, pages, likes, and comments.
views.py specifies how the site renders templates as you navigate around.
utils.py contains some utilities for fetching posts, comments, friendships, pages/events/groups, etc, and a function for creating them.




Notes/sources:

This final project includes reused code from Projects 3 and 4.
It includes most of the Project 4 template, as well as reused JS files which I previously wrote for Mail and Network.
