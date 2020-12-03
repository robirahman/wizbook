document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);
  document.querySelector('#send').addEventListener('click', send_email);

  // By default, load the inbox
  load_mailbox('inbox');
});

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#message-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}

function load_mailbox(mailbox) {

  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#message-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';

  // Fetch <mailbox> and get response.json() and emails
  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {
    emailsHTML = "";
    emails.forEach((email)=>{
      if (mailbox == 'sent') {
        // Don't show From in Sent mailbox
        var tofrom = `To: ${email['recipients']} / `;
      } else {
        // Don't show To in Inbox or Archive
        var tofrom = `From: ${email['sender']} / `;
      }
      emailsHTML += `<div id="${email['id']}" onclick="show_email('${mailbox}', '${email['id']}');" data-read=${email['read']}>`
                  + tofrom
                  + `Subject: ${email['subject']} / `
                  + `Date: ${email['timestamp']}</div>`
    });
    document.querySelector('#emails-view').innerHTML += emailsHTML;
  });



  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3><br />`;
}

function send_email(event) {
  // Save form contents to variables
  email_recipients = document.querySelector("#compose-recipients").value;
  email_subject = document.querySelector("#compose-subject").value;
  email_body = document.querySelector("#compose-body").value;
  
  const invalid = "Email was not delivered to one or more recipient(s) due to invalid or unregistered address. "
                + "Please verify the intended destination email address(es) and try again.";
  // POST message to the API to save into database
  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
        recipients: email_recipients,
        subject: email_subject,
        body: email_body
    })
  })
  .then(response => {
    if (response.status === 400) {
      alert(invalid);
    } else {
      response.json();
      load_mailbox('sent');
    }
  })
  event.preventDefault();
}

function reply(emailid) {

  // Fetch email #emailid
  fetch(`/emails/${emailid}`)
  .then(response => response.json())
  .then(email => {
    const recipient = email['sender'];
    let subject = email['subject'];
    const body = email['body'];
    const date = email['timestamp'];
    if (subject.startsWith("Re: ")) {
      // pass
    } else {
      subject = `Re: ${subject}`;
    }
    // Show compose view and hide other views
    document.querySelector('#emails-view').style.display = 'none';
    document.querySelector('#message-view').style.display = 'none';
    document.querySelector('#compose-view').style.display = 'block';
    // Pre-fill composition fields
    document.querySelector('#compose-recipients').value = recipient;
    document.querySelector('#compose-subject').value = subject;
    document.querySelector('#compose-body').value = `\n\nOn ${date}, ${recipient} wrote: ${body}`;
  })
}

function show_email(mailbox, emailid) {

  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#message-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';

  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails =>{
    var email = Object.values(emails).find(x => x.id == emailid);
    if (email['archived'] == true) {
      // If email in Archive, button says Restore
      document.querySelector('#archive').innerHTML = "Restore";
    } else {
      // If email in Inbox, button says Archive
      document.querySelector('#archive').innerHTML = "Archive";
    }
    message = `From: ${email['sender']}<br />`
            + `To: ${email['recipients']}<br />`
            + `Subject: ${email['subject']}<br />`
            + `Date: ${email['timestamp']}<br />`
            + `Message: ${email['body']}`;
    document.querySelector('#message').innerHTML = message;
    document.querySelector('#archive').addEventListener('click', () => archive(email));
    document.querySelector('#reply').addEventListener('click', () => reply(email['id']));              
  });
  fetch(`/emails/${emailid}`, {
    method: 'PUT',
    body: JSON.stringify({read: true})
  });
}

function archive(email) {
  fetch(`/emails/${email['id']}`, {
    method: 'PUT',
    body: JSON.stringify({archived: !email['archived']})
  });
  location.reload();
  return false;
}