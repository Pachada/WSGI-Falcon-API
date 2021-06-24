import smtplib, ssl
import configparser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from models.EmailSent import EmailSent
from models.EmailPool import EmailPool
from datetime import datetime
from models.Status import Status

class SmtpClientCrontab():

    __instance = None

    @staticmethod
    def get_instance():
        if not SmtpClientCrontab.__instance:
            SmtpClientCrontab()
        return SmtpClientCrontab.__instance

    def __init__(self):
        if SmtpClientCrontab.__instance is not None:
            return SmtpClientCrontab.__instance
        else:
            SmtpClientCrontab.__instance = self
            self.config = configparser.ConfigParser()
            self.config.read('config.ini')
            self.username = self.config.get('SMTP', 'username')
            self.port = self.config.get('SMTP', 'port')
            self.password = self.config.get('SMTP', 'password')
            self.server = self.config.get('SMTP', 'server')
            self.fromemail = self.config.get('SMTP', 'fromemail')
            self.context = ssl.create_default_context()

    def send_email(self, query_limit:int):
        emails_to_send = []
        try:
            with smtplib.SMTP(self.server, self.port) as server:
                server.starttls(context=self.context)
                server.login(self.username, self.password)
                list_of_emails = EmailPool.getAll(filter = EmailPool.status_id.in_([Status.PENDING, Status.ERROR]), limit=query_limit)
                errors = 0
                for email in list_of_emails:
                    email:EmailPool = email
                    email.status_id =  Status.PROCESSING 
                    email.save()
                    emails_to_send.append(email)

                for email in emails_to_send:
                    email:EmailPool = email
                    msg, content = self.__create_message(email)
                    response_code = server.sendmail(self.fromemail, email.email, msg)

                    if not response_code:
                        email.delete()
                    else:
                        errors += 1
                        email.status_id = Status.ERROR
                        email.send_attemps = email.send_attemps + 1
                        email.save()

                    self.__save_to_sended(content, email.email, email.template_id, response_code)
                    
                selected = len(emails_to_send)
                send = selected - errors
                print(f'Date and time: {datetime.now().strftime("%d/%b/%Y %H:%M:%S")}, selected: {selected}, sended: {send}, errores: {errors}')
        except Exception as exc:
            print(exc)
            print("Error sending email")
            if emails_to_send:
                for email in emails_to_send:
                    email.status_id = Status.ERROR
                    email.save()
            return False

    def __create_message(self, email:EmailPool):
        msg = MIMEMultipart()
        msg['Subject'] = email.subject
        msg['From'] = self.fromemail
        msg['To'] = email.email
        msg.attach(MIMEText(email.content, "html"))
        return msg.as_string(), email.content

    def __save_to_sended(self, msg:str, email:str, template_id:int, codes):
        send = Status.ERROR
        code = str(codes)
        
        if not codes:
            send = Status.SEND
            code = "250: Requested mail action okay, completed"
            
        email = EmailSent(template_id = template_id, content = msg, email = email, send = send, code = code)
        email.save()


def main():
    client = SmtpClientCrontab.get_instance()
    client.send_email(50)

if __name__ == "__main__":
    main()
