from onesignal_sdk.client import Client
from onesignal_sdk.error import OneSignalHTTPError
import configparser
from core.Utils import Utils
from core.classes.PushNotificationUtils import (
    PushNotificationUtils,
    Status,
    Device,
    PushNotificationPool,
)


class PushNotificationCrontabOneSignal(PushNotificationUtils):
    __instance = None
    max_send_attempts = 3

    @staticmethod
    def get_instance():
        if not PushNotificationCrontabOneSignal.__instance:
            return PushNotificationCrontabOneSignal()
        return PushNotificationCrontabOneSignal.__instance

    def __init__(self):
        if PushNotificationCrontabOneSignal.__instance is not None:
            return PushNotificationCrontabOneSignal.__instance

        PushNotificationCrontabOneSignal.__instance = self
        self.config = configparser.ConfigParser()
        self.config.read(Utils.get_config_ini_file_path())
        self.app_id = self.config.get("ONESIGNAL", "app_id")
        self.api_key = self.config.get("ONESIGNAL", "api_key")
        self.client = Client(self.app_id, self.api_key)

    def send_notification_to_all_users(self, notification: PushNotificationPool):
        try:
            notification_body = {
                "contents": {"en": notification.message},
                "included_segments": ["Subscribed Users"],  # Subscribed Users
            }

            self.client.send_notification(notification_body)
            notification.delete()
            return 0

        except OneSignalHTTPError as e:  # An exception is raised if response.status_code != 2xx
            print("[ERROR SENDING NOTIFICATION TO ALL USERS")
            print(e.message)
            notification.status_id = Status.ERROR
            notification.save()
            return 1

    def send_messages(self, data: dict[PushNotificationPool, Device]):
        errors = 0
        for push_notification, device in data.items():
            try:
                push_notification: PushNotificationPool = push_notification

                notification_body = {
                    "contents": {"en": push_notification.message},
                    "include_player_ids": [device.token],
                }

                # Make a request to OneSignal
                self.client.send_notification(notification_body)

            except OneSignalHTTPError as e:  # An exception is raised if response.status_code != 2xx
                print(e)
                self.notification_with_errors(push_notification)
                errors += 1
            except Exception as e:
                print(e)
                self.notification_with_errors(push_notification)
                errors += 1
            else:
                push_notification.delete()

        return errors

    def main(self, query_limit):
        self.send_push_notifications(query_limit)


if __name__ == "__main__":
    client = PushNotificationCrontabOneSignal.get_instance()
    client.procces_pool(5000)
