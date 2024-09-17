import configparser
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from core.classes.NotificationCronsUtils import NotificationCronsUtils, Utils
from models.EmailPool import EmailPool
from models.EmailSent import EmailSent


class SmtpClientCrontab(NotificationCronsUtils):
    config = configparser.ConfigParser()
    config.read(Utils.get_config_ini_file_path())

    def __init__(self):
        self.username = self.config.get("SMTP", "username")
        self.port = self.config.get("SMTP", "port")
        self.password = self.config.get("SMTP", "password")
        self.server = self.config.get("SMTP", "server")
        self.fromemail = self.config.get("SMTP", "fromemail")

        self.email_pools_to_delete: list[EmailPool] = []

    def send_emails(self, query_limit: int):
        emails_to_send = self.get_rows_to_send(EmailPool, query_limit)
        if not emails_to_send:
            self.nothing_to_send()
            return

        self.put_rows_in_proccesing_status(emails_to_send)

        with smtplib.SMTP(self.server, self.port) as server:
            server.starttls(context=ssl.create_default_context())
            server.login(self.username, self.password)
            errors = sum(self.send_email(server, email) for email in emails_to_send)
            if self.email_pools_to_delete:
                EmailPool.delete_multiple(EmailPool.id.in_([email.id for email in self.email_pools_to_delete]))
            self.show_results(len(emails_to_send), errors)

    def create_message(self, email_pool: EmailPool) -> str:
        msg = MIMEMultipart()
        msg["Subject"] = email_pool.subject
        msg.attach(MIMEText(email_pool.content, "html"))
        return msg.as_string()

    def save_to_sent(self, msg: str, email: str, template_id: int):
        email_sent = EmailSent(
            email=email,
            template_id=template_id,
            content=msg
        )
        if not email_sent.save():
            print("[ERROR SAVING SENT EMAIL]")

    def send_email(self, server: smtplib.SMTP, email_pool: EmailPool) -> int:
        email = email_pool.email
        error = not Utils.check_if_valid_email(email)

        if not error:
            msg = self.create_message(email_pool)
            response_code = server.sendmail(self.fromemail, email, msg)
            if response_code:
                error = True

        if error:
            self.row_with_errors(email_pool)
            return 1

        self.save_to_sent(email_pool.content, email, email_pool.template_id)
        self.email_pools_to_delete.append(email)
        return 0

    def send_one_email(self, email_pool: EmailPool):
        with smtplib.SMTP(self.server, self.port) as server:
            server.starttls(context=ssl.create_default_context())
            server.login(self.username, self.password)
            error = self.send_email(server, email_pool)
            if not error and self.email_pools_to_delete:
                EmailPool.delete(self.email_pools_to_delete[0].id)
            self.show_results(1, error)

    def main(self, limit: int = 5000):
        self.send_emails(limit)


if __name__ == "__main__":
    client = SmtpClientCrontab()
    client.procces_pool(5000)
