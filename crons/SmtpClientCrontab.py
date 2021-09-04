import smtplib, ssl
import configparser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from models.EmailSent import EmailSent, and_
from models.EmailPool import EmailPool
from datetime import datetime
from models.Status import Status
from core.Utils import Utils


class SmtpClientCrontab:

    __instance = None
    max_send_attempts = 3

    @staticmethod
    def get_instance():
        if not SmtpClientCrontab.__instance:
            SmtpClientCrontab()
        return SmtpClientCrontab.__instance

    def __init__(self):
        if SmtpClientCrontab.__instance is not None:
            return SmtpClientCrontab.__instance

        SmtpClientCrontab.__instance = self
        self.config = configparser.ConfigParser()
        self.config.read(Utils.get_config_ini_file_path())
        self.username = self.config.get("SMTP", "username")
        self.port = self.config.get("SMTP", "port")
        self.password = self.config.get("SMTP", "password")
        self.server = self.config.get("SMTP", "server")
        self.fromemail = self.config.get("SMTP", "fromemail")

        self.context = ssl.create_default_context()

    def send_emails(self, query_limit: int):
        emails_to_send = []
        try:
            with smtplib.SMTP(self.server, self.port) as server:
                server.starttls(context=self.context)
                server.login(self.username, self.password)

                emails_to_send = self.__get_emails_to_send(query_limit)

                if not emails_to_send:
                    print(
                        f'Date and time: {Utils.today_in_tz().strftime("%d/%b/%Y %H:%M:%S")}, No emails to send'
                    )
                    return

                self.__put_emails_in_proccesing_stratus(emails_to_send)

                errors = sum(
                    self.__send_email(server, email) for email in emails_to_send
                )
                selected = len(emails_to_send)
                send = selected - errors
                print(
                    f'Date and time: {Utils.today_in_tz().strftime("%d/%b/%Y %H:%M:%S")}, selected: {selected}, sended: {send}, errores: {errors}'
                )
        except Exception as exc:
            print(exc)
            print("Error sending email")
            if emails_to_send:
                for email in emails_to_send:
                    self.__email_with_errors(email)

    def __create_message(self, email: EmailPool):
        msg = MIMEMultipart()
        msg["Subject"] = email.subject
        msg["From"] = self.fromemail
        msg["To"] = email.email
        msg.attach(MIMEText(email.content, "html"))
        return msg.as_string(), email.content

    def __save_to_sended(self, msg: str, email: str, template_id: int, codes):
        send = Status.ERROR
        code = str(codes)

        if not codes:
            send = Status.SEND
            code = "250: Requested mail action okay, completed"

        email = EmailSent(
            template_id=template_id, content=msg, email=email, status_id=send, code=code
        )
        email.save()

    def __get_emails_to_send(self, query_limit):
        return EmailPool.getAll(
            and_(
                EmailPool.status_id.in_([Status.PENDING, Status.ERROR]),
                EmailPool.send_time <= datetime.utcnow(),
                EmailPool.send_attemps < self.max_send_attempts,
            ),
            limit=query_limit,
        )

    def __put_emails_in_proccesing_stratus(self, data):
        for email in data:
            email: EmailPool = email
            email.status_id = Status.PROCESSING
            email.save()

    def __email_with_errors(self, email: EmailPool):
        email.status_id = Status.ERROR
        email.send_attemps = email.send_attemps + 1
        email.save()
        if email.send_attemps >= self.max_send_attempts:
            email.delete()

    def __send_email(self, server: smtplib.SMTP, email: EmailPool):
        error = False
        if not Utils.check_if_valid_email(email.email):
            error = True

        if not error:
            msg, content = self.__create_message(email)
            response_code = server.sendmail(self.fromemail, email.email, msg)
            if response_code:
                error = True

        if error:
            self.__email_with_errors(email)
            return 1

        self.__save_to_sended(content, email.email, email.template_id, response_code)
        email.delete()

        return 0


def main():
    client = SmtpClientCrontab.get_instance()
    client.send_emails(50)


if __name__ == "__main__":
    main()
