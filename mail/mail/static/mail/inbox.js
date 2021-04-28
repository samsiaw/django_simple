// TODO: Handle all errors
document.addEventListener('DOMContentLoaded', function () {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  //Submitting an email
  document.querySelector("#compose-form").addEventListener('submit', submit_email);

  // By default, load the inbox
  // TODO: Display compose email page if there's an error with composing
  load_mailbox('inbox');
});

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';
  document.querySelector('#info-view').style.display = 'none';
  clear_view("info-view");
  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}

function load_mailbox(mailbox) {
  clear_view(mailbox);
    // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;
  get_mails(mailbox);

  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#info-view').style.display = 'none';
  clear_view("info-view");

  
}

function submit_email() {

  // Get data from forms
  // REVIEW: Recipient(s) - Handle mutliple recipients
  const recipients = document.querySelector("#compose-recipients").value;
  const subject = document.querySelector("#compose-subject").value;
  const body = document.querySelector("#compose-body").value;

  // Post data to server
  
  let rlist = extract_rec(recipients);
  console.log("rlist: "+ rlist);
  for (var i=0; i<rlist.length; i++){
    submit_single(rlist[i], subject, body);
  }

}

function submit_single(recipient, subject, body){
  fetch("/emails", {
    method: 'POST',
    body: JSON.stringify(
      {
        recipients: recipient,
        subject: subject,
        body: body
      }
    )
  })
  .then(resp => resp.json())
  .then(res => {

    //console.log(res);
    if (res['error'] === undefined){
      alert(res['message']);

      } else {
        alert(res['error']);
      }
  });
}
/**
 * Function displays a list of mails queried from
 * server
 * @param {json} mailbox 
 */
function get_mails(mailbox){
 
  // Get latest mails from server
  fetch(`/emails/${mailbox}`)
  .then(resp => resp.json())
  .then(mails_json => {
      //console.log(mails_json);
      if (mails_json.error === undefined){
      
      if (mailbox === 'sent'){
        heading = single_mail_display(mailbox, "Recipient", "Subject", "Date/Time", null, false);
      }
      else{
      heading = single_mail_display(mailbox, "Sender", "Subject", "Date/Time", null, false);
      }
      document.querySelector("#emails-view").append(
        heading
      );
      headingClone = heading.cloneNode(true); //Removes eventListeners on element
      heading.parentNode.replaceChild(headingClone, heading); //Replace with new clone
      headingClone.style.borderColor = "white";
      headingClone.style.cursor = "context-menu";

        //Iterate through JSON to get all mails
          for (var i =0; i<mails_json.length; i++){
            mail = mails_json[i];
            const id = mail.id;
            const sender = mail.sender;
            const subject = mail.subject;
            const time = mail.timestamp;
            const read = mail.read;
            const recipient = mail.recipients;
            
            if (mailbox === 'sent'){
              var m = single_mail_display(mailbox, recipient, subject, time, id, read);
            }
            else{
            var m = single_mail_display(mailbox, sender, subject, time, id, read);
            }
            document.querySelector("#emails-view").append( m );

          }
        }
        else{
          alert(mails_json.error);
        }
      }
    );
  }

function single_mail_display(mailbox, sender, subject, time, id, read){
  let single_mail = document.createElement('div');
  const sen = document.createElement('div');
  const subj = document.createElement('div');
  const tim = document.createElement('div');
  single_mail.append(sen, subj, tim);

  sen.innerHTML = `<b>${sender}</b>`;
  subj.innerHTML = `<b>${subject}</b>`;
  tim.innerHTML = `${time}`;

  single_mail.classList.add("s-mail");
  //single_mail.href = ``;

  if (read === true){
    single_mail.style.backgroundColor = "lightgrey";
  }

  single_mail.addEventListener("click",() => info_view(id, mailbox));


  return single_mail;
}

/**
 * 
 * @param {int} id 
 * @param {json} mailbox 
 */
function info_view(id, mailbox){
  // Mark as read
  mark(id, r=true, a=null);

  // Get json of current clicked mail
  fetch(`emails/${id}`)
  .then(resp => resp.json())
  .then(mail => {

    // Display info on email
    email_view = view_mail(mail, mailbox);
    let info_view = document.querySelector('#info-view');
    //document.querySelector('#info-view').innerHTML = email_view.innerHTML;
    info_view.append(email_view); // TODO: Delete current child if 
    // Close emails-view and compose-view and open info-view
    info_view.style.display = 'flex';
    document.querySelector('#emails-view').style.display = 'none';
    document.querySelector('#compose-view').style.display = 'none';

    //Style info-view
    info_view.style.flexFlow = "column wrap";
  });

}

function view_mail(mail, mailbox){

  function view_mail_helper(bold_text, data){
    div = document.createElement('div');
    div.innerHTML = `<b>${bold_text}</b>: ${data}`;
    return div;
  }

  const id = mail.id;
  const sender = mail.sender;
  const subject = mail.subject;
  const time = mail.timestamp;
  const body = mail.body;
  const recipients = mail.recipients;
  const archived = mail.archived;

  info_page = document.createElement('div');
  body_view = document.createElement('div');
  email_info = document.createElement('div');
  hr = document.createElement('hr');

  info_page.append(email_info, hr, body_view);

  email_info.appendChild(view_mail_helper("From", sender));
  // REVIEW: You may have to re-write a display for recipientS.
  email_info.appendChild(view_mail_helper("To", recipients));
  email_info.appendChild(view_mail_helper("Subject", subject));
  email_info.appendChild(view_mail_helper("Timestamp", time));
  body_view.innerHTML = body;

  // BUTTON GROUP - Reply, Archive
  // Display reply and archive buttons on the page
  //(If current mailbox is 'Sent', don't display 'Archive button' )
  button_group = document.createElement('div');
  button_group.classList.add("button-group");

  reply_b = document.createElement('button');
  button_group.append(reply_b);
  reply_b.classList.add("btn", "btn-outline-primary", "btn-sm", "btn-helper");
  reply_b.innerHTML = "Reply";
  reply_b.onclick = () => reply_func(subject, body, sender, time);

  if (mailbox !== "sent"){
    archive_b = document.createElement('button');
    button_group.append(archive_b);
    archive_b.classList.add("btn", "btn-outline-primary", "btn-sm");
    if (archived){
      archive_b.innerHTML = "Unarchive";
    }
    else{
      archive_b.innerHTML = "Archive";
    }
    archive_b.onclick = () => archive_func(id, archived);
  }
  // TODO: Add funcs to the buttons
  email_info.append(button_group);
    
  return info_page;
}


function clear_view(mailbox){
  if (mailbox === "info-view"){
   view = document.querySelector("#info-view");
  }
  else{
    view = document.querySelector("#emails-view");
  }
  
    let child = view.firstElementChild;
    while (child){
      view.removeChild(child);
      child = view.firstElementChild;
    }
  
}

function mark(id, r, a){
  if (r !== null){
    fetch(`/emails/${id}`,
    {
      method: 'PUT',
      body: JSON.stringify({
        read: r
      })
    }
    )
  }
  if (a !== null){
    fetch(`/emails/${id}`,
    {
      method: 'PUT',
      body: JSON.stringify({
        archived: a
      })
    }
    )
  }
}

function archive_func(id, archived){
  //alert(`called archive_func: archive -> ${archived}`);
  if (archived === true){
    mark(id, r=null, a=false);
  }
  else{
    mark(id, r=null, a=true);
  }

  load_mailbox('archive');
}

function reply_func(subject, body, sender, time){
  compose_email();

  // REVIEW: Might have to rewrite 
  // recipents to fill in info appropriately
  document.querySelector('#compose-recipients').value = sender;
  subject = subject.trim();
  if (subject.length > 2 && subject.slice(0, 3).toLowerCase() === "re:"){
      document.querySelector('#compose-subject').value = `${subject}`;
   }
  else{
    document.querySelector('#compose-subject').value = `Re: ${subject}`;
  }

  document.querySelector('#compose-body').value = `On ${time} ${sender} wrote: ${body}&#13;&#10`;
}
function extract_rec(rec){
  let rList = rec.split(/\s+|;/);
  let res = [];
  for (var i=0; i<rList.length; i++ ){
  	let r = rList[i];
    if (r.trim() !== ""){
      res.push(r);
    }
  }
  return res;
}