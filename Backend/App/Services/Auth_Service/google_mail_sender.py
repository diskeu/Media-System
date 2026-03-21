# Class for the sending of email-authentication-mails to the Client

# Basic Test Script

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient import errors
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from Backend.App.Services.Auth_Service.verification_mail import build_verification_mail

class MailSender():
    SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
    def __init__(
            self,
            port: int=0,
            token_f_location="Backend/Configurations/token.json",
            credentials_f_location="/Users/TimJelenz/Desktop/messenger/Backend/Configurations/credentials.json",
            ):
        """
        Loads the acces tokens and trys to connect to the Apps-Script-Api.
        'Backend/Configurations/token.json' stores the User's access and refresh tokens,
        and is created automatically when the authorization flow completes for the first time.\n
        NOTE: Class should only used once in initalisation and parsed to other funcs because it
        isn't asynchron.
        
        Param:
            - port -> port where flow 'll get run
            - token_f_location -> location where the acces/refresh tokens will be/are stored
            - credentials_f_location -> location where the app identity get's stored

        Raises:
            - google.auth.exceptions.RefreshError if the scope is invalid
        """
        self.port = port
        self.token_f_location = token_f_location
        self.credentials_f_location = credentials_f_location

        creds = None
        if os.path.exists("Backend/Configurations/token.json"):
            creds = Credentials.from_authorized_user_file(token_f_location, MailSender.SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                credentials_f_location, MailSender.SCOPES
                )
                creds = flow.run_local_server(port=port)
            # writing changes to file
            with open(token_f_location, "w") as token_f:
                token_f.write(creds.to_json())

    def update_scope(self,*args) -> None:
        """
        Function to update SCOPES with given urls\n
        Function 'll automaticlly refresh the token_f_location
        """
        map(MailSender.SCOPES.append, args)
        flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_f_location, MailSender.SCOPES
                )
        creds = flow.run_local_server(port=self.port)
        # writing changes to file
        with open(self.token_f_location, "w") as token_f:
            token_f.write(creds.to_json())

    def send_mail(user_name: str):
        """Sends Mail using the defined mail in verification_mail.py"""
        body = build_verification_mail(user_name)
        
