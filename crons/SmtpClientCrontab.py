import smtplib, ssl
import configparser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from models.EmailSent import EmailSent
from models.EmailPool import EmailPool, User
from core.classes.NotificationCronsUtils import NotificationCronsUtils, Utils


class SmtpClientCrontab(NotificationCronsUtils):

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

    def send_emails(self, query_limit: int):
        emails_to_send = []
        try:
            # Start the smtp server with the credential in config.ini
            with smtplib.SMTP(self.server, self.port) as server:
                server.starttls(context=ssl.create_default_context())
                server.login(self.username, self.password)

                emails_to_send = self.get_rows_to_send(EmailPool, query_limit)

                if not emails_to_send:
                    self.nothing_to_send()
                    return

                self.put_rows_in_proccesing_status(emails_to_send)

                errors = sum(
                    self.__send_email(server, email) for email in emails_to_send
                )

                self.show_results(len(emails_to_send), errors)
                
        except Exception as exc:
            print(exc)
            print("Error sending emails")
            if emails_to_send:
                for email in emails_to_send:
                    self.row_with_errors(email)

    def __create_message(self, email_pool: EmailPool):
        msg = MIMEMultipart()
        msg["Subject"] = email_pool.subject
        msg.attach(MIMEText(email_pool.content, "html"))
        return msg.as_string()

    def __save_to_sended(self, msg: str, user_id: int, template_id: int):

        email = EmailSent(
            user_id=user_id,
            template_id=template_id,
            content=msg
        )
        if not email.save():
            print("[ERROR SAVING SENDED EMAIL]")

    def __send_email(self, server: smtplib.SMTP, email_pool: EmailPool):
        """Send the email
        Returs 1 if there was an error, 0 otherwise
        """
        user: User = email_pool.user
        error = not Utils.check_if_valid_email(user.email)

        if not error:
            msg = self.__create_message(email_pool)
            # If the email was sended with out errors it will return an empty dict
            response_code = server.sendmail(self.fromemail, user.email, msg)
            if response_code:
                error = True

        if error:
            self.row_with_errors(email_pool)
            return 1

        # The email was sended, save it to the sended records and delete the EmailPool object
        self.__save_to_sended(
            email_pool.content, user.id, email_pool.template_id
        )
        email_pool.delete()

        return 0

    def main(self, limit = 5000):
        self.send_emails(limit)


if __name__ == "__main__":
    client = SmtpClientCrontab.get_instance()
    client.procces_pool(5000)
