document.addEventListener('DOMContentLoaded', function() {

    try {
      document.querySelector('#post').addEventListener('click', writePost);
      document.querySelector('#new-post').addEventListener('click', showPostBox);
    } catch(error) {
      console.log("No post form on this page.");
      // console.log(error);
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
      console.log("No posts on this page.");
      // console.log(error);
    }
    try {
      document.querySelectorAll('.edit').forEach(pencil => {
        pencil.addEventListener('click', showEditBox);
      });
    } catch(error) {
      console.log("No editable posts on this page.");
    }
    try {
      document.querySelectorAll('#create').forEach(link => {
        link.addEventListener('click', showCreateBox);
      });
    } catch(error) {
      console.log("Cannot create page/event/group here.");
      console.log(error);
    }

    document.querySelector('#create-peg').style.display = 'none';  


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
        alert("Tweet not posted.");
      } else {
        response.json();
        window.location.href = "";
      }
    });
    event.preventDefault();
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

function showPostBox(event) {
    document.querySelector('#post-box').style.display = 'block';
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
