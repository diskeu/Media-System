# Tests for the MailSender class

from Backend.App.Services.Auth_Service.google_mail_sender import MailSender

mail_sender = MailSender( # -> Works
    port=0
)

# Mail Debug Loop
import smtplib

with smtplib.SMTP("localhost", 1025) as smtp:
    smtp.sendmail(
        "from@test.com",
        "to@test.com",
        "Subject: Test\n\nHello World!"
    )