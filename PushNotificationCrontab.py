from exponent_server_sdk import (
    DeviceNotRegisteredError,
    PushClient,
    PushMessage,
    PushServerError,
    PushTicketError,
    PushTicket
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

class PushNotificationCrontab():
    __instance = None

    @staticmethod
    def get_instance():
        if not PushNotificationCrontab.__instance:
            PushNotificationCrontab()
        return PushNotificationCrontab.__instance
    
    def __init__(self):
        if PushNotificationCrontab.__instance is not None:
            return PushNotificationCrontab.__instance
        else:
            PushNotificationCrontab.__instance = self

    def send_push_notifications(self, query_limit):
        notifications_to_process = []
        try:
            list_of_notifications_to_send = PushNotificationPool.getAll(
                and_(
                    PushNotificationPool.status_id.in_([Status.PENDING, Status.ERROR]),
                    PushNotificationPool.send_attemps < 3
                ),
                limit=query_limit
                )

            if not list_of_notifications_to_send:
                print(f'Date and time: {str(datetime.now())[0:-7]}, no notifications to send.')
                return
            
            for notification in list_of_notifications_to_send:
                notification:PushNotificationPool = notification
                notification.status_id = Status.PROCESSING
                notification.save()
                notifications_to_process.append(notification)
            
            errors = 0
            notifications_to_send:dict = {}
            for notification in notifications_to_process:
                error = False
                private_notifiaction = False
                notification:PushNotificationPool = notification
                
                # Send notifications to the device associated with the last session of the user 
                # check if the user has a valid sessions if the notification template is private.
                template:PushNotificationTemplate = notification.template
                if template.private:
                    private_notifiaction = True

                last_session = Session.max("updated", Session.user_id == notification.user_id)
                session = Session.get(Session.updated == last_session)
                if not session:
                    error = True
                
                if not error:    
                    device:Device = session.device
                    # if the notifications is private check if the sessions is valid 
                    # Check that the device has an token 
                    if private_notifiaction and not Utils.validate_session(session):
                        error = True
                    if not device.token:
                        error = True
                
                if error:
                    notification.status_id = Status.ERROR
                    errors += 1
                    notification.send_attemps = notification.send_attemps + 1
                    notification.save()
                    continue
                    
                # The sessión has a valid device and the device of that session has a token
                notifications_to_send[notification] = device
                
            errors += self.__send_push_messages(notifications_to_send)
            selected = len(notifications_to_process)
            send = selected - errors
            print(f'Date and time: {str(datetime.now())[0:-7]}, selected: {selected}, send: {send}, errors: {errors}')

        except Exception as exc:
            print(exc)
            print("Error sending push notifications")
            if notifications_to_process:
                notification:PushNotificationPool
                for notification in notifications_to_process:
                    notification.status_id = Status.ERROR
                    notification.save()

    # Send PushNotification to multiple tokens
    def __send_push_messages(self, data:dict):
        errors = 0
        try:
            error = False
            push_messages = []
            for push_notification, device in data.items():
                push_notification:PushNotificationPool = push_notification
                device:Device = device
                message = PushMessage(
                    to = device.token,
                    body = push_notification.message,
                    data = json.loads(push_notification.data)
                )
                push_messages.append(message)

            push_tickets = PushClient().publish_multiple(push_messages)
            # Lets associate the ticket with the PushNotificationPool
            for (push_notification, _), ticket in zip(data.items(), push_tickets):
                push_notification:PushNotificationPool = push_notification
                ticket:PushTicket = ticket
                push_notification.ticket = ticket.id
                push_notification.save()

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
                push_notification:PushNotificationPool = push_notification
                push_notification.status_id = Status.ERROR
                push_notification.save()
                errors += 1
            return errors

        # We got a response back, but we don't know whether it's an error yet.
        # This call raises errors so we can handle them with normal exception
        # flows.
        for ticket in push_tickets:
            try:
                ticket:PushTicket = ticket
                push_notification = PushNotificationPool.get(PushNotificationPool.ticket == ticket.id)
                device:Device = data[push_notification]
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
                push_notification.status = Status.ERROR
                push_notification.send_attemps = push_notification.send_attemps + 1
                push_notification.save()
                errors += 1

            self.__save_to_sended(push_notification, device, comments)
        return errors


    def __save_to_sended(self, push_notification:PushNotificationPool, device:Device=None, comments=None ):
        push_notification_send = PushNotificationSent(
            user_id = push_notification.user_id,
            device_id = device.id if device else None,
            template_id = push_notification.template_id,
            ticket = push_notification.ticket if push_notification.ticket else None,
            message = push_notification.message,
            data = push_notification.data,
            idStatus = push_notification.status_id,
            comments = comments if comments else None
        )
        push_notification_send.save()

def main(query_limit):
    client = PushNotificationCrontab.get_instance()
    client.send_push_notifications(query_limit)


if __name__ == '__main__':
    main(100)