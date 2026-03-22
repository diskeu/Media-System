# Class for the sending of email-authentication-mails to the Client
import os.path
import threading
from asyncio import get_running_loop
from base64 import urlsafe_b64encode

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.message import EmailMessage
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
        NOTE: Class should only used once in initalisation and parsed to other funcs because it
        isn't asynchron.
        
        Param:
            - port -> port where flow 'll get run
            - token_f_location -> location where the acces/refresh tokens will be/are stored
            - credentials_f_location -> location where the app identity get's stored
        """
        self.port = port
        self.token_f_location = token_f_location
        self.credentials_f_location = credentials_f_location

    def authenticate(self) -> Credentials:
        """
        Loads the acces tokens and trys to connect to the Apps-Script-Api.
        When the creds in self.token_f_location are valid the authorization finishes without doing further steps.
        'Backend/Configurations/token.json' stores the User's access and refresh tokens,
        and is created automatically when the authorization flow completes for the first time.

        Raises:
            - google.auth.exceptions.RefreshError if the scope is invalid

        Returns:
            - the Credentials to operate with the api
        """
        creds = None
        if os.path.exists(self.token_f_location):
            creds = Credentials.from_authorized_user_file(self.token_f_location, MailSender.SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_f_location, MailSender.SCOPES
                )
                creds = flow.run_local_server(port=self.port)
            # writing changes to file
            with open(self.token_f_location, "w") as token_f:
                token_f.write(creds.to_json())
        return creds

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

    def _send_mail(self, user_name: str, user_email: str):
        """Sends Mail using the defined mail in verification_mail.py and returns the api's json return in dict format"""

        # getting html
        body = build_verification_mail(user_name)
        
        # Building msg
        msg = EmailMessage()
        msg.set_content(body, subtype="html")

        msg["Subject"] = "Confirm your Media-System account"
        msg["FROM"] = "marvinmagmud@gmail.com"
        msg["TO"] = user_email

        # convert to raw format
        raw = urlsafe_b64encode(msg.as_bytes()).decode()

        # getting credentials
        creds = self.authenticate()

        # Connectiong script to gmail - api and sending mail
        with build("gmail", "v1", credentials = creds) as service:
            return service.users().messages().send( # -> operates on user's account-messages
                userId = "me",
                body = {"raw": raw}
            ).execute()
        
    async def send_mail_async(self, user_name: str, user_email: str):
        """Wrapper for the synchronous _send_mail function. Short Documentation in '_send_mail'."""
        # Running _send_mail in current event loop
        loop = get_running_loop()
        future = loop.run_in_executor(None, self._send_mail, user_name, user_email)
        return await future