import base64
import json

import sys

import requests
from email.mime.text import MIMEText

from gmail_auth_service import get_gmail_service, reauthenticate

def create_message(sender,
                   to,
                   subject,
                   previous_references,
                   previous_message_id,
                   thread_id,
                   message_text):
    message = MIMEText(message_text, "html", "ASCII")
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    # No idea if this is correct.  What a mysterious thing MIME is.
    message["In-Reply-To"] = previous_message_id
    if previous_references:
        message["References"] = previous_references + " " + previous_message_id
    else:
        message["References"] = previous_message_id

    return {
        "raw": base64.urlsafe_b64encode(message.as_string().encode("ASCII")).decode("ASCII"),
        "threadId": thread_id
    }


def send_message(service, message):
    return service.users().messages().send(userId="me", body=message).execute()


def dump_inbox(service):
    response = service.users().messages().list(userId="me",
                                               labelIds="INBOX").execute()
    messages = []
    if 'messages' in response:
        messages.extend(response['messages'])

    while 'nextPageToken' in response:
        page_token = response['nextPageToken']
        response = service.users().messages().list(userId="me",
                                                   labelIds="INBOX",
                                                   pageToken=page_token).execute()
        messages.extend(response['messages'])

    return messages


def archive_message(service, message_id):
    label_changes = {'removeLabelIds': ['UNREAD', 'INBOX'], 'addLabelIds': []}
    service.users().messages().modify(userId="me",
                                      id=message_id,
                                      body=label_changes).execute()


def get_relevant_headers(service, message_id):
    message_data = service.users().messages().get(userId="me",
                                                 id=message_id,
                                                 format="metadata").execute()
    headers = message_data["payload"]["headers"]

    def get_header_value(name):
        try:
            return next(h["value"] for h in headers if h["name"].lower() == name)
        except StopIteration:
            return None

    return (lambda names: {name: get_header_value(name) for name in names})(
        ["from", "subject", "message-id", "references"])


def process_messages(service):
    for new_message in dump_inbox(service):
        headers = get_relevant_headers(service, new_message["id"])
        print("Processing message from {}".format(headers["from"]))
        archive_message(service, new_message["id"])
        email_content = build_email_content(get_random_cat_gif())
        send_message(service, create_message("Colin.Bumtrousers@gmail.com",
                                             headers["from"],
                                             headers["subject"],
                                             headers["references"],
                                             headers["message-id"],
                                             new_message["threadId"],
                                             email_content))


def get_random_cat_gif():
    def get_url(url):
        response = requests.get(url)
        response.raise_for_status()
        return response.content

    return json.loads(get_url("http://api.giphy.com/v1/gifs/random?api_key=dc6zaTOxFJmzC&tag=cat")
                         .decode("UTF-8"))["data"]["image_url"]


def build_email_content(gif_url):
    return """<html>
        <h1>Greetings from Mr Colin B. Trousers</h1>
        <br/>
        <img style="display:block;margin-left:auto;margin-right:auto;" src="{}"/>
    </html>
    """.format(gif_url)


def main():
    service=get_gmail_service()
    process_messages(service)


if __name__ == '__main__':
    if sys.argv[1:] and sys.argv[1] == "reauth":
        reauthenticate()
    else:
        main()
