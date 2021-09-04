from onesignal_sdk.client import Client
from onesignal_sdk.error import OneSignalHTTPError
from requests.exceptions import ConnectionError, HTTPError
import configparser
from datetime import datetime
from sqlalchemy import or_, and_
from core.Utils import Utils
from models.PushNotificationTemplate import PushNotificationTemplate
from models.PushNotificationPool import PushNotificationPool
from models.User import User
from models.Device import Device
from models.Status import Status

class PushNotificationCrontabOneSignal():
    __instance = None

    @staticmethod
    def get_instance():
        if not PushNotificationCrontabOneSignal.__instance:
            PushNotificationCrontabOneSignal()
        return PushNotificationCrontabOneSignal.__instance
    
    def __init__(self):
        if PushNotificationCrontabOneSignal.__instance is not None:
            return PushNotificationCrontabOneSignal.__instance
        else:
            PushNotificationCrontabOneSignal.__instance = self
            self.config = configparser.ConfigParser()
            self.config.read(Utils.get_config_ini_file_path())
            self.app_id = self.config.get('ONESIGNAL', 'app_id')
            self.api_key = self.config.get('ONESIGNAL', 'api_key')
            self.client = Client(self.app_id, self.api_key)

    def send_push_notifications(self, query_limit):
        notifications_to_process = []
        try:
            list_of_notifications_to_send = PushNotificationPool.getAll(
                and_(
                    PushNotificationPool.status_id.in_([Status.PENDING, Status.ERROR]),
                    PushNotificationPool.send_attemps < 3,
                    PushNotificationPool.notification_time <= datetime.utcnow()
                ),
                limit=query_limit
                )

            if not list_of_notifications_to_send:
                print(f'Date time: {datetime.now().strftime("%d/%b/%Y %H:%M:%S")}, no notifications to send.')
                return
            
            for notification in list_of_notifications_to_send:
                notification:PushNotificationPool = notification
                notification.status_id = Status.PROCESSING
                notification.save()
                notifications_to_process.append(notification)
            
            errors = 0
            notifications_to_send:dict = {}
            for notification in notifications_to_process:
                notification:PushNotificationPool = notification
                template:PushNotificationTemplate = notification.template

                # if the template of the notification is not private, send it to all users
                if not template.private:
                    errors += self.__send_notification_to_all_users(notification)
                    continue

                # Send notifications to all the device of the user 
                error = False
                user:User = notification.user
                user_devices = Device.getAll(and_(
                    Device.user_id == user.id,
                    Device.token != None
                ))
                if not user_devices:
                    error = True
                
                if error:
                    notification.status_id = Status.ERROR
                    errors += 1
                    notification.send_attemps = notification.send_attemps + 1
                    notification.save()
                    continue
                    
                notifications_to_send[notification] = user_devices
                
            errors += self.__send_push_messages(notifications_to_send)
            selected = len(notifications_to_process)
            send = selected - errors
            print(f'Date time: {datetime.now().strftime("%d/%b/%Y %H:%M:%S")}, selected: {selected}, sended: {send}, errors: {errors}')

        except Exception as exc:
            print(exc)
            print("Error sending push notifications")
            if notifications_to_process:
                notification:PushNotificationPool
                for notification in notifications_to_process:
                    notification.status_id = Status.ERROR
                    notification.save()

    def __send_notification_to_all_users(self, notification:PushNotificationPool):
        try:
            notification_body = {
                'contents': {'en': notification.message},
                'included_segments': ['Subscribed Users'] # Subscribed Users
            }

            response = self.client.send_notification(notification_body)
            notification.status_id = Status.SEND
            notification.soft_delete()
            notification.save()
            return 0

        except OneSignalHTTPError as e: # An exception is raised if response.status_code != 2xx
            print("[ERROR SENDING NOTIFICATION TO ALL USERS")
            print(e.message)
            notification.status_id = Status.ERROR
            notification.save()
            return 1

    # Send PushNotifications
    def __send_push_messages(self, data:dict):
        errors = 0
        for push_notification, devices in data.items():
            try:
                push_notification:PushNotificationPool = push_notification
                device_to_send = [device.token for device in devices]

                notification_body = {
                    'contents': {'en': push_notification.message},
                    'include_player_ids': device_to_send
                }

                # Make a request to OneSignal
                self.client.send_notification(notification_body)

            except OneSignalHTTPError as e: # An exception is raised if response.status_code != 2xx
                print(e)
                push_notification.status_id = Status.ERROR
                push_notification.send_attemps = push_notification.send_attemps + 1
                push_notification.save()
                errors += 1
            except Exception as exc:
                continue
            else:
                push_notification.status_id = Status.SEND
                push_notification.soft_delete()
        return errors
                

def main(query_limit):
    client = PushNotificationCrontabOneSignal.get_instance()
    client.send_push_notifications(query_limit)


if __name__ == '__main__':
    main(100)