from exponent_server_sdk import (
    DeviceNotRegisteredError,
    PushClient,
    PushMessage,
    PushServerError,
    PushTicketError,
    PushTicket,
)
from requests.exceptions import ConnectionError, HTTPError
import json
from core.classes.PushNotificationCronUtils import (
    PushNotificationCronUtils,
    Device,
    PushNotificationPool
)


class ExpoPushNotificationCrontab(PushNotificationCronUtils):
    __instance = None

    @staticmethod
    def get_instance():
        if not ExpoPushNotificationCrontab.__instance:
            return ExpoPushNotificationCrontab()
        return ExpoPushNotificationCrontab.__instance

    def __init__(self):
        if ExpoPushNotificationCrontab.__instance is not None:
            return ExpoPushNotificationCrontab.__instance

        ExpoPushNotificationCrontab.__instance = self
    
    def send_notification_to_all_users(self, notification: PushNotificationPool):
        # TODO Send the notification to all users
        notification.delete()
        print("ERROR SENDING PUSH NOTIFICATION TO ALL USERS TO EXPO SERVER")
        print(
            "The way to send notification to all users for the moment \
            is to call the PushNotificationClient.send_notification_to_pool with the \
            user parameter containen a list of all users."
        )
        return 1

    def send_messages(self, data: dict[PushNotificationPool, Device]):
        """
        Send PushNotification to multiple tokens using Expo server
        """
        errors = 0
        try:
            error = False
            push_messages = []
            for push_notification, device in data.items():
                message = PushMessage(
                    to=device.token,
                    body=push_notification.message,
                    data=json.loads(push_notification.data),
                )
                push_messages.append(message)

            push_tickets = PushClient().publish_multiple(push_messages)

        except PushServerError as exc:
            # Encountered some likely formatting/validation error.
            print(exc)
            error = True

        except (ConnectionError, HTTPError) as exc:
            # Encountered some Connection or HTTP error
            print(exc)
            error = True

        if error:
            print("Error sendind push notifications to Expo server")
            for push_notification in data:
                self.notification_with_errors(push_notification)
                errors += 1
            return errors

        # We got a response back, but we don't know whether it's an error yet.
        # This call raises errors so we can handle them with normal exception
        # flows.
        errors += self.__validate_notification_response(push_tickets, data)

        return errors

    def __validate_notification_response(self, push_tickets: list[PushTicket], data: dict[PushNotificationPool, Device]):
        errors = 0
        for (push_notification, device), ticket in zip(data.items(), push_tickets):
            try:
                error = False

                ticket.validate_response()

                self.save_to_sended(push_notification, device)
                push_notification.delete()

            except DeviceNotRegisteredError:
                # Mark the push token as inactive
                error = True
                device.token = None
                device.save()

            except PushTicketError as exc:
                # Encountered some other per-notification error.
                error = True

            if error:
                self.notification_with_errors(push_notification)
                errors += 1

        return errors

    def main(self, query_limit):
        self.send_push_notifications(query_limit)


if __name__ == "__main__":
    client = ExpoPushNotificationCrontab.get_instance()
    client.procces_pool(5000)
