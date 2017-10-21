import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client.file import Storage


SCOPES = " ".join(["https://www.googleapis.com/auth/gmail.readonly",   # Reading messages
                   "https://www.googleapis.com/auth/gmail.send",       # Sending messages
                   "https://www.googleapis.com/auth/gmail.modify"])    # Archiving messages.
CLIENT_SECRET_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "client_secret.json")
APPLICATION_NAME = 'Gmail API Python Quickstart'


def get_gmail_service():
    credentials = get_credentials(get_credential_store())
    http = credentials.authorize(httplib2.Http())
    return discovery.build('gmail', 'v1', http=http)

def reauthenticate():
    store = get_credential_store()

    flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
    flow.user_agent = APPLICATION_NAME
    flow.redirect_uri = client.OOB_CALLBACK_URN

    print('Auth URL: ' + flow.step1_get_authorize_url())
    code = input('Enter verification code: ').strip()
    credential = flow.step2_exchange(code, http=httplib2.Http())

    store.put(credential)
    credential.set_store(store)

    print('Authentication successful.')


def get_credential_store():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'gmail-python-quickstart.json')
    store = Storage(credential_path)
    return store


def get_credentials(store):
    credentials = store.get()
    if not credentials or credentials.invalid:
        raise RuntimeError("Invalid Credentials")
    return credentials
