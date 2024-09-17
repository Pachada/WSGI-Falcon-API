from models.PushNotificationPool import (
    PushNotificationPool,
    Status,
    datetime,
    PushNotificationTemplate,
    and_,
)
from models.Session import Session, Device, Utils
from models.PushNotificationSent import PushNotificationSent


class PushNotificationCronUtils:
    """
    Utils methos for Push Notification Crontabs
    """

    max_send_attempts = 3

    def main(limit):
        raise NotImplementedError

    def procces_pool(self, limit: int = 10):
        """Start the sending procces"""
        self.main(limit)

    def get_notifications_to_send(self, query_limit):
        return PushNotificationPool.get_all(
            and_(
                PushNotificationPool.status_id.in_([Status.PENDING, Status.ERROR]),
                PushNotificationPool.send_time <= datetime.utcnow(),
            ),
            limit=query_limit,
        )

    def put_notifications_in_processing_status(self, data: list):
        for notification in data:
            notification: PushNotificationPool = notification
            notification.status_id = Status.PROCESSING
        
        PushNotificationPool.save_all(data)

    def get_last_sessions(self, notification: PushNotificationPool):
        session = Session.get_all(
            Session.user_id == notification.user_id,
            order_by=Session.updated.desc(),
            limit=1
        )
        if not session:
            return

        session: Session = session[0]
        return session

    def validate_device_token_and_valid_session(
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
        private_notifiaction = bool(template.private)
        #
        # if the notifications is private check if the sessions is valid
        device: Device = session.device
        if not device.token or (
            private_notifiaction and not Utils.validate_expiration_time(session.updated, "session")
        ):
            return device, True

        return device, False

    def notification_with_errors(self, notification: PushNotificationPool):
        notification.send_attemps += 1
        if notification.send_attemps >= self.max_send_attempts:
            notification.delete()
            return

        notification.status_id = Status.ERROR
        notification.save()

    def send_push_notifications(self, query_limit):
        notifications_to_process = []
        try:
            notifications_to_process = self.get_notifications_to_send(query_limit)

            if not notifications_to_process:
                print(f'Date time: {Utils.today_in_tz().strftime("%d/%b/%Y %H:%M:%S")}, no notifications to send.')
                return

            self.put_notifications_in_processing_status(notifications_to_process)

            errors = 0
            notifications_to_send: dict = {}
            tokens = set()
            for notification in notifications_to_process:
                notification: PushNotificationPool = notification
                template: PushNotificationTemplate = notification.template

                # if the template is not private, and the notification_pool does not
                # have a user, send it to all users
                if not template.private and not notification.user_id:
                    errors += self.send_notification_to_all_users(notification)
                    continue

                # Send the  notification to the device associated with the last session of the user
                session = self.get_last_sessions(notification)

                error = not session
                if not error:
                    device, error = self.validate_device_token_and_valid_session(
                        session, notification
                    )

                if error:
                    errors += 1
                    self.notification_with_errors(notification)
                    continue

                # If the token of the device is in tokens, continue
                if device.token in tokens:
                    continue

                tokens.update(device.token)

                # The sessión has a valid device and the device of that session has a token
                notifications_to_send[notification] = device

            errors += self.send_messages(notifications_to_send)
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
                    self.notification_with_errors(notification)

    def send_notification_to_all_users(self, notification: PushNotificationPool):
        # Implemented in subclass
        raise NotImplementedError

    def send_messages(self, notifications_to_send):  # notifications_to_send: dict[PushNotificationPool, Device]
        # Implemented in subclass
        raise NotImplementedError

    def save_to_sended(
        self, push_notification: PushNotificationPool, device: Device = None
    ):
        push_notification_send = PushNotificationSent(
            user_id=push_notification.user_id,
            device_id=device.id if device else None,
            template_id=push_notification.template_id,
            message=push_notification.message
        )

        push_notification_send.save()
