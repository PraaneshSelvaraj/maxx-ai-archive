from __future__ import print_function
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly','https://www.googleapis.com/auth/contacts.readonly']


def build_service(name):
    if not name: return None
    creds = None

    if os.path.exists('./includes/token.json'):
        creds = Credentials.from_authorized_user_file('./includes/token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                './includes/googlecred.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('./includes/token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        if name == "calendar":
            service = build('calendar', 'v3', credentials=creds)
            return service

        elif name == "people":
            service = build('people', 'v1', credentials=creds)
            return service

    except HttpError as error:
        print('An error occurred: %s' % error)

