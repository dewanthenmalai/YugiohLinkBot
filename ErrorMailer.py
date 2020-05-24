import smtplib, ssl
from email.message import EmailMessage
import Config
import MailConfig

def SendErrorMail(e, stacktrace):
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(MailConfig.SMTPserver, MailConfig.SMTPport, context=context) as server:
        server.login(Config.botemail, Config.emailpassword)
        
        message = EmailMessage()
        message.set_content(MailConfig.mailformat.format(
            type = type(e),
            message = str(e),
            stacktrace = stacktrace
        ))
        message['Subject'] = MailConfig.subject
        message['From'] = Config.botemail
        message['To'] = [Config.adminemail, Config.botemail]

        server.send_message(message)