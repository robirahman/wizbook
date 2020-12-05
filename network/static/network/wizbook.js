document.addEventListener('DOMContentLoaded', function() {

    try {
      document.querySelector('#post').addEventListener('click', writePost);
      document.querySelector('#new-post').addEventListener('click', showPostBox);
      document.querySelector('#cancel').addEventListener('click', hidePostBox);
    } catch(error) {
      console.log("No post form on this page.");
    }
    try {
      document.querySelector('#comment-box').style.display = 'none';
    } catch(error) {
      console.log("No comment form on this page.");
    }
    try {
      document.querySelector('#follow').addEventListener('click', follow);
    } catch(error) {
      console.log("No follow button on this page.");
      // console.log(error);
    }
    try {
      document.querySelectorAll('.like').forEach(heart => {
        heart.addEventListener('click', like)
      });
    } catch(error) {
      console.log("No likeable posts on this page.");
    }
    try {
      document.querySelectorAll('.edit').forEach(pencil => {
        pencil.addEventListener('click', showEditBox);
      });
    } catch(error) {
      console.log("No editable posts on this page.");
    }
    try {
      document.querySelectorAll('.comment').forEach(bubble => {
        bubble.addEventListener('click', showCommentBox);
      });
    } catch(error) {
      console.log("Nowhere to comment on this page.");
    }
    try {
      document.querySelectorAll('#create').forEach(link => {
        link.addEventListener('click', showCreateBox);
      });
    } catch(error) {
      console.log("Cannot create page/event/group here.");
      console.log(error);
    }
    try {
      document.querySelector('#create-peg').style.display = 'none';
    } catch(error) {
      console.log('No page/event/group form on this page.');
    }
  
  });
  

function writePost(event) {
    // Save form contents to variable
    postBody = document.querySelector('#post-body').value;
    
    // POST message to the API to save into database
    fetch('/post', {
      method: 'POST',
      body: JSON.stringify({
          body: postBody
      })
    })
    .then(response => {
      if (response.status === 400) {
        alert("Message was not posted.");
      } else {
        response.json();
        window.location.href = "";
      }
    });
    event.preventDefault();
  }


function showPostBox(event) {
  document.querySelector('#post-box').style.display = 'block';
  event.preventDefault();
}

function hidePostBox(event) {
  document.querySelector('#post-box').style.display = 'none';
  event.preventDefault();
}

function showEditBox(event) {
  postId = event.target.id.slice(4);
  let postBody = document.querySelector(`#post${postId}`);
  document.querySelector('#edit-body').innerHTML = postBody.innerHTML;
  let editAnchor = document.querySelector(`#edit${postId}`);
  let editBox = document.querySelector('#edit-box');
  const parentPost = editAnchor.parentElement;
  parentPost.append(editBox);
  editBox.style.display = 'block';
  saveButton = document.querySelector('#save-edit');
  saveButton.addEventListener('click', saveEdit);
  saveButton.dataset.target = `${postId}`;
  event.preventDefault();
  return false;
}

function showCommentBox(event) {
  postId = event.target.id.slice(7);
  let commentBody = document.querySelector(`#comment${postId}`);
  let commentAnchor = document.querySelector(`#post${postId}`);
  let commentBox = document.querySelector('#comment-box');
  const parentPost = commentAnchor.parentElement;
  parentPost.append(commentBox);
  commentBox.style.display = 'block';
  commentButton = document.querySelector('#save-comment');
  commentButton.addEventListener('click', saveComment);
  commentButton.dataset.target = `${postId}`;
  event.preventDefault();
  return false;
}

function saveEdit(event) {
  editBox = document.querySelector('#edit-box');
  editBody = document.querySelector('#edit-body');
  // Save form contents to variable
  postBody = editBody.value;
  postId = document.querySelector('#save-edit').dataset.target;

  // POST to the API to save the edited text
  fetch(`/post/${postId}/edit`, {
    method: 'POST',
    body: JSON.stringify({
      body: postBody,
      id: postId
    })
  })
  .then(response => {
    if (response.status === 400) {
      alert("Post not saved.");
    } else {
      response.json();
      document.querySelector(`#post${postId}`).innerHTML = postBody;
      editBox.style.display = 'none';
    }
  });
  event.preventDefault();
  return false;
}
function saveComment(event) {
  commentBox = document.querySelector('#comment-box');
  commentBody = document.querySelector('#comment-body');
  // Save form contents to variable
  commentText = commentBody.value;
  postId = document.querySelector('#save-comment').dataset.target;

  // POST to the API to save the comment
  fetch(`/post/${postId}/comment`, {
    method: 'POST',
    body: JSON.stringify({
      text: commentText,
      id: postId
    })
  })
  .then(response => {
    if (response.status === 400) {
      alert("Comment not saved.");
    } else {
      response.json();
      console.log("Need to append the comment to the post here.");
      commentBox.style.display = 'none';
    }
  });
  alert("Need to reload page or have JS update comments that are shown.");
  event.preventDefault();
  return false;
}

function showCreateBox(event) {
  // need to set form's display style to block
  document.querySelector('#create-peg').style.display = 'block'; 
  document.querySelector('#listings').style.display = 'none';
  console.log(event);
  event.preventDefault();
}

function follow(event) {
  let followButton = document.querySelector('#follow');
  let followAnchor = document.querySelector('#followers');
  const followTarget = followButton.dataset.target;
  let numFollowers =  followAnchor.dataset.followers;
  const token = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
  fetch(`/users/${followTarget}/follow`, {
    method: 'PUT',
    body: JSON.stringify({follow: "True"}),
    headers: {
      "X-CSRFToken": token
    }
  })
  .then(response => response.json())
  .then(data => {
    numFollowers = data['newFollowers'];
    followAnchor.innerHTML = `${numFollowers}`;
    if (data['result'] == "unfollowed") {
      followButton.innerHTML = "Follow";
    } else if (data['result'] == "followed") {
      followButton.innerHTML = "Unollow";
    }
  });
  event.preventDefault;
  return false;
}

function like(event) {
  postId = event.target.id.slice(4);
  let likeAnchor = document.querySelector(`#likes${postId}`);
  numLikes = likeAnchor.innerHTML;
  const token = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
  fetch(`/post/${postId}/like`, {
    method: 'PUT',
    body: JSON.stringify({like: "True"}),
    headers: {
      "X-CSRFToken": token
    }
  })
  .then(response => response.json())
  .then(data => {
    console.log(data);
    numLikes = data['newLikes'];
    likeAnchor.innerHTML = `${numLikes}`;
  });
  event.preventDefault();
  return false;
}
