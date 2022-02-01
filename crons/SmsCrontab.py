import configparser
from models.SmsSent import SmsSent
from models.SmsPool import SmsPool, User
from core.classes.NotificationCronsUtils import NotificationCronsUtils, Utils
from core.classes.aws.SnsHandler import SnsHandler


class SmsCrontab(NotificationCronsUtils):

    __instance = None

    @staticmethod
    def get_instance():
        return SmsCrontab() if not SmsCrontab.__instance else SmsCrontab.__instance

    def __init__(self):
        if SmsCrontab.__instance is not None:
            return SmsCrontab.__instance

        SmsCrontab.__instance = self
        self.config = configparser.ConfigParser()
        self.config.read(Utils.get_config_ini_file_path())
        self.client = SnsHandler(self.config.get("SNS", "region"))

    def send_sms(self, query_limit: int):
        sms_to_send = []
        try:
                sms_to_send = self.get_rows_to_send(SmsPool, query_limit)

                if not sms_to_send:
                    self.nothing_to_send()
                    return

                self.put_rows_in_proccesing_status(sms_to_send)

                errors = sum(
                    self.__send_messages(sms_pool) for sms_pool in sms_to_send
                )

                self.show_results(len(sms_to_send), errors)
                
        except Exception as exc:
            print(exc)
            print("Error sending sms")
            if sms_to_send:
                for sms in sms_to_send:
                    self.row_with_errors(sms)

    def __save_to_sended(self, sms_pool: SmsPool, user: User):

        sms = SmsSent(
            user_id=user.id,
            template_id=sms_pool.template_id,
            message=sms_pool.message
        )
        if not sms.save():
            print("[ERROR SAVING SENDED EMAIL]")

    def __send_messages(self, sms_pool: SmsPool):
        """Send the sms
        Returs 1 if there was an error, 0 otherwise
        """
        user: User = sms_pool.user
        error = not Utils.check_if_valid_ten_digits_number(user.phone)

        if not error:
            # If the sms was sended with out errors it will return an id
            # None otherwise
            sms_id = self.client.publish_text_message(user.phone, sms_pool.message)
            if not sms_id:
                error = True

        if error:
            self.row_with_errors(sms_pool)
            return 1

        # The sms was sended, save it to the sended records and delete the SmsPool object
        self.__save_to_sended(
            sms_pool, user
        )
        sms_pool.delete()

        return 0

    def main(self, query_limit):
        self.send_sms(query_limit)


if __name__ == "__main__":
    client = SmsCrontab.get_instance()
    client.main(5000)
