document.addEventListener('DOMContentLoaded', function() {

    try {
      document.querySelector('#croak').addEventListener('click', writePost);
      document.querySelector('#new-post').addEventListener('click', showCroakBox);
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
      // console.log(error);
    }
    
  });
  

function writePost(event) {
    // Save form contents to variable
    postBody = document.querySelector("#post-body").value;
    
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
      alert("Croak not saved.");
    } else {
      response.json();
      document.querySelector(`#croak${postId}`).innerHTML = postBody;
      editBox.style.display = 'none';
    }
  });
  event.preventDefault();
  return false;
}

function showCroakBox(event) {
    document.querySelector('#croak-box').style.display = 'block';
    event.preventDefault();
}

function showEditBox(event) {
  postId = event.target.id.slice(4);
  let croakBody = document.querySelector(`#croak${postId}`);
  document.querySelector('#edit-body').innerHTML = croakBody.innerHTML;
  let editAnchor = document.querySelector(`#edit${postId}`);
  let editBox = document.querySelector('#edit-box');
  const parentCroak = editAnchor.parentElement;
  parentCroak.append(editBox);
  editBox.style.display = 'block';
  saveButton = document.querySelector('#save-edit');
  saveButton.addEventListener('click', saveEdit);
  saveButton.dataset.target = `${postId}`;
  event.preventDefault();
  return false;
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
