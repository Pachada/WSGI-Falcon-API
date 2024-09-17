import configparser

from onesignal_sdk.client import Client
from onesignal_sdk.error import OneSignalHTTPError

from core.classes.PushNotificationCronUtils import (Device,
                                                    PushNotificationCronUtils,
                                                    PushNotificationPool,
                                                    Status)
from core.Utils import Utils


class OneSignalPushNotificationCrontab(PushNotificationCronUtils):
    __instance = None

    @staticmethod
    def get_instance():
        if not OneSignalPushNotificationCrontab.__instance:
            return OneSignalPushNotificationCrontab()
        return OneSignalPushNotificationCrontab.__instance

    def __init__(self):
        if OneSignalPushNotificationCrontab.__instance is not None:
            return OneSignalPushNotificationCrontab.__instance

        OneSignalPushNotificationCrontab.__instance = self
        self.config = configparser.ConfigParser()
        self.config.read(Utils.get_config_ini_file_path())
        self.app_id = self.config.get("ONESIGNAL", "app_id")
        self.api_key = self.config.get("ONESIGNAL", "api_key")
        self.client = Client(self.app_id, self.api_key)

    def send_notification_to_all_users(self, notification: PushNotificationPool):
        try:
            notification_body = {
                "contents": {"en": notification.message},
                "included_segments": ["Subscribed Users"],
            }

            self.client.send_notification(notification_body)
            notification.delete()
            return 0

        except OneSignalHTTPError as e:
            print("[ERROR SENDING NOTIFICATION TO ALL USERS")
            print(e.message)
            notification.status_id = Status.ERROR
            notification.save()
            return 1

    def send_messages(self, data):  # data: dict[PushNotificationPool, Device]
        errors = 0
        for push_notification, device in data.items():
            try:
                push_notification: PushNotificationPool = push_notification

                notification_body = {
                    "contents": {"en": push_notification.message},
                    "include_player_ids": [device.token],
                }

                self.client.send_notification(notification_body)

            except OneSignalHTTPError as e:
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
    client = OneSignalPushNotificationCrontab.get_instance()
    client.main(5000)
