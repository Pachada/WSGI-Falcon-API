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
            return SmtpClientCrontab()
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

    @staticmethod
    def procces_pool(limit: int = 10):
        """Start the email sending procces"""
        main(limit)

    def send_emails(self, query_limit: int):
        emails_to_send = []
        try:
            # Start the smtp server with the credential in config.ini
            with smtplib.SMTP(self.server, self.port) as server:
                server.starttls(context=ssl.create_default_context())
                server.login(self.username, self.password)

                emails_to_send = self.__get_emails_to_send(query_limit)

                if not emails_to_send:
                    print(
                        f'Date and time: {Utils.today_in_tz().strftime("%d/%b/%Y %H:%M:%S")}, No emails to send'
                    )
                    return

                self.__put_emails_in_proccesing_status(emails_to_send)

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
            print("Error sending emails")
            if emails_to_send:
                for email in emails_to_send:
                    self.__email_with_errors(email)

    def __create_message(self, email: EmailPool):
        msg = MIMEMultipart()
        msg["Subject"] = email.subject
        msg["From"] = self.fromemail
        msg["To"] = email.email
        msg.attach(MIMEText(email.content, "html"))
        return msg.as_string()

    def __save_to_sended(self, msg: str, email: str, template_id: int):
        code = "250: Sended"

        email = EmailSent(
            template_id=template_id,
            content=msg,
            email=email,
            status_id=Status.SEND,
            code=code,
        )
        if not email.save():
            print("[ERROR SAVING SENDED EMAIL]")

    def __get_emails_to_send(self, query_limit):
        return EmailPool.get_all(
            and_(
                EmailPool.status_id.in_([Status.PENDING, Status.ERROR]),
                EmailPool.send_time <= datetime.utcnow(),
                # EmailPool.send_attemps < self.max_send_attempts  - Los que superen el limite se borran
            ),
            limit=query_limit,
        )

    def __put_emails_in_proccesing_status(self, data: list):
        for email in data:
            email: EmailPool = email
            email.status_id = Status.PROCESSING
            if not email.save():
                data.remove(email)

    def __email_with_errors(self, email: EmailPool):
        email.send_attemps += 1
        if email.send_attemps >= self.max_send_attempts:
            email.delete()
            return

        email.status_id = Status.ERROR
        email.save()

    def __send_email(self, server: smtplib.SMTP, email_pool: EmailPool):
        """Send the email
        Returs 1 if there was an error, 0 otherwise
        """
        error = not Utils.check_if_valid_email(email_pool.email)

        if not error:
            msg = self.__create_message(email_pool)
            response_code = server.sendmail(self.fromemail, email_pool.email, msg)
            if response_code:
                error = True

        if error:
            self.__email_with_errors(email_pool)
            return 1

        # The email was sended, save it to the sended records and delete the EmailPool object
        self.__save_to_sended(
            email_pool.content, email_pool.email, email_pool.template_id
        )
        email_pool.delete()

        return 0


def main():
    client = SmtpClientCrontab.get_instance()
    client.send_emails(5000)


if __name__ == "__main__":
    main()
