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
from datetime import datetime
from sqlalchemy import or_, and_
from core.Utils import Utils
from models.PushNotificationPool import PushNotificationPool
from models.PushNotificationSent import PushNotificationSent
from models.Device import Device
from models.Session import Session
from models.Status import Status
from models.PushNotificationTemplate import PushNotificationTemplate


class ExpoPushNotificationCrontab:
    __instance = None

    @staticmethod
    def get_instance():
        if not ExpoPushNotificationCrontab.__instance:
            ExpoPushNotificationCrontab()
        return ExpoPushNotificationCrontab.__instance

    def __init__(self):
        if ExpoPushNotificationCrontab.__instance is not None:
            return ExpoPushNotificationCrontab.__instance
        else:
            ExpoPushNotificationCrontab.__instance = self

    def send_push_notifications(self, query_limit):
        notifications_to_process = []
        try:
            notifications_to_process = self.__get_notifications_to_send(query_limit)

            if not notifications_to_process:
                print(
                    f'Date time: {Utils.today_in_tz().strftime("%d/%b/%Y %H:%M:%S")}, no notifications to send.'
                )
                return

            self.__put_notifications_in_processing_status(notifications_to_process)

            errors = 0
            notifications_to_send: dict = {}
            for notification in notifications_to_process:
                error = False
                # Send the  notification to the device associated with the last session of the user
                session = self.__get_last_sessions(notification)

                if not session:
                    error = True

                if not error:
                    device, error = self.__validate_device_token_and_valid_session(
                        session, notification
                    )

                if error:
                    errors += 1
                    self.__notification_with_errors(notification)
                    continue

                # The sessión has a valid device and the device of that session has a token
                notifications_to_send[notification] = device

            errors += self.__send_push_notifications_to_expo_server(
                notifications_to_send
            )
            selected = len(notifications_to_process)
            send = selected - errors
            print(
                f'Date time: {Utils.today_in_tz().strftime("%d/%b/%Y %H:%M:%S")}, selected: {selected}, sended: {send}, errors: {errors}'
            )

        except Exception as exc:
            print(exc)
            print("Error sending push notifications")
            if notifications_to_process:
                for notification in notifications_to_process:
                    self.__notification_with_errors(notification)

    def __send_push_notifications_to_expo_server(self, data: dict):
        """
        Send PushNotification to multiple tokens using Expo server
        """
        errors = 0
        try:
            error = False
            push_messages = []
            for push_notification, device in data.items():
                push_notification: PushNotificationPool = push_notification
                device: Device = device
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
                self.__notification_with_errors(push_notification)
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
            push_notification.send_attemps = push_notification.send_attemps + 1
            push_notification.save()
            comments = "Sended"

        except DeviceNotRegisteredError:
            # Mark the push token as inactive
            error = True
            device.token = None
            device.save()
            push_notification.soft_delete()
            comments = "Device not registered error"

        except PushTicketError as exc:
            # Encountered some other per-notification error.
            error = True
            comments = "push ticket error"

        if error:
            self.__notification_with_errors(push_notification)
            errors += 1

        self.__save_to_sended(push_notification, device, comments)

        return errors

    def __save_to_sended(
        self,
        push_notification: PushNotificationPool,
        device: Device = None,
        comments=None,
    ):
        push_notification_send = PushNotificationSent(
            user_id=push_notification.user_id,
            device_id=device.id if device else None,
            template_id=push_notification.template_id,
            push_notification_pool_id=push_notification.id,
            ticket=push_notification.ticket or None,
            message=push_notification.message,
            data=push_notification.data,
            status_id=push_notification.status_id,
            comments=comments or None,
        )

        push_notification_send.save()

    def __associate_tickets_with_their_notifications(
        self, data: dict, push_tickets: list
    ):
        for (push_notification, _), ticket in zip(data.items(), push_tickets):
            push_notification: PushNotificationPool = push_notification
            ticket: PushTicket = ticket
            push_notification.ticket = ticket.id
            push_notification.save()

    def __get_notifications_to_send(self, query_limit):
        return PushNotificationPool.getAll(
            and_(
                PushNotificationPool.status_id.in_([Status.PENDING, Status.ERROR]),
                PushNotificationPool.send_attemps < 3,
                PushNotificationPool.notification_time <= datetime.utcnow(),
            ),
            limit=query_limit,
        )

    def __put_notifications_in_processing_status(self, data: list):
        for notification in data:
            notification: PushNotificationPool = notification
            notification.status_id = Status.PROCESSING
            if not notification.save():
                data.remove(notification)

    def __get_last_sessions(self, notification: PushNotificationPool):
        last_session_time = Session.max(
            "updated", Session.user_id == notification.user_id
        )
        return Session.get(
            and_(
                Session.updated == last_session_time,
                Session.user_id == notification.user_id,
            )
        )

    def __validate_device_token_and_valid_session(
        self, session: Session, notification: PushNotificationPool
    ):
        """
        Checks if the device of the session has a token
        And if the notification template is private, check if the session is valid

        Returns
        ----------
        `Device`
            The device to send the notification to
        `bool`
            True if there was any error, otherwise False
        """
        template: PushNotificationTemplate = notification.template
        private_notifiaction = False
        if template.private:
            private_notifiaction = True

        #
        # if the notifications is private check if the sessions is valid
        device: Device = session.device
        if not device.token or (
            private_notifiaction and not Utils.validate_session(session)
        ):
            return device, True

        return device, False

    def __notification_with_errors(self, notification: PushNotificationPool):
        notification.status_id = Status.ERROR
        notification.send_attemps = notification.send_attemps + 1
        notification.save()


def main(query_limit):
    client = ExpoPushNotificationCrontab.get_instance()
    client.send_push_notifications(query_limit)


if __name__ == "__main__":
    main(250)
