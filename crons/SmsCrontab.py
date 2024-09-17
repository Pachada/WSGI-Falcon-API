import configparser

from core.classes.aws.SnsHandler import SnsHandler
from core.classes.NotificationCronsUtils import NotificationCronsUtils, Utils
from models.SmsPool import SmsPool, User
from models.SmsSent import SmsSent


class SmsCrontab(NotificationCronsUtils):
    config = configparser.ConfigParser()
    config.read(Utils.get_config_ini_file_path())

    def __init__(self):
        self.client = SnsHandler(self.config.get("SNS", "region"))

    def send_sms(self, query_limit: int):
        sms_to_send = self.get_rows_to_send(SmsPool, query_limit)
        if not sms_to_send:
            self.nothing_to_send()
            return

        errors = sum(self.send_message(sms_pool) for sms_pool in sms_to_send)
        self.show_results(len(sms_to_send), errors)

    def save_to_sent(self, sms_pool: SmsPool, user: User):
        sms = SmsSent(
            user_id=user.id,
            template_id=sms_pool.template_id,
            message=sms_pool.message
        )
        if not sms.save():
            print("[ERROR SAVING SENT SMS]")

    def send_message(self, sms_pool: SmsPool) -> int:
        user: User = sms_pool.user
        error = not Utils.check_if_valid_ten_digits_number(user.phone)

        if not error:
            sms_id = self.client.publish_text_message(user.phone, sms_pool.message)
            if not sms_id:
                error = True

        if error:
            self.row_with_errors(sms_pool)
            return 1

        self.save_to_sent(sms_pool, user)
        sms_pool.delete()

        return 0

    def send_one_sms(self, sms_pool: SmsPool):
        try:
            error = self.send_message(sms_pool)
            self.show_results(1, error)
        except Exception as exc:
            print(exc)
            print("Error sending sms")
            self.row_with_errors(sms_pool)

    def main(self, query_limit: int):
        self.send_sms(query_limit)


if __name__ == "__main__":
    client = SmsCrontab()
    client.main(5000)
