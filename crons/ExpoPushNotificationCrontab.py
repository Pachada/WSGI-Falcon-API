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
from core.classes.PushNotificationUtils import (
    PushNotificationUtils,
    Status,
    Device,
    PushNotificationPool,
)


class ExpoPushNotificationCrontab(PushNotificationUtils):
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
            # Lets associate the ticket with the PushNotificationPool
            self.__associate_tickets_with_their_notifications(data, push_tickets)

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
        for ticket in push_tickets:
            errors += self.__validate_notification_response(ticket, data)

        return errors

    def __validate_notification_response(self, ticket, data):
        errors = 0
        try:
            ticket: PushTicket = ticket
            push_notification = PushNotificationPool.get(
                PushNotificationPool.ticket == ticket.id
            )
            device: Device = data[push_notification]
            error = False

            ticket.validate_response()

            push_notification.status_id = Status.SEND
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

    def __associate_tickets_with_their_notifications(
        self, data: dict, push_tickets: list
    ):
        for (push_notification, _), ticket in zip(data.items(), push_tickets):
            push_notification: PushNotificationPool = push_notification
            ticket: PushTicket = ticket
            push_notification.ticket = ticket.id
            push_notification.save()

    def main(self, query_limit):
        self.send_push_notifications(query_limit)


if __name__ == "__main__":
    client = ExpoPushNotificationCrontab.get_instance()
    client.procces_pool(5000)
