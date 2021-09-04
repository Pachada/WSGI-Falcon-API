from datetime import datetime, timedelta
from models.User import User, and_
from models.Session import Session
from models.PushNotificationTemplate import PushNotificationTemplate
from core.classes.PushNotificationClient import PushNotificationClient
import pytz


class ReminderCrontab():

    def remind_users_to_play(self):
        today = datetime.utcnow()
        delta = today - timedelta(days=7)

        sessions = Session.getAll(Session.updated < delta)

        if not sessions:
            print(f"{today.strftime('%d/%b/%Y %H:%M:%S')} No hay usuarios que recordar")
            return

        user_ids = []
        client = PushNotificationClient.get_instance()
        for session in sessions:
            user: User = session.user
            # Check if users have a valid sessions, if the do, do not send notification to them
            last_user_session_value = Session.max("updated", Session.user_id == user.id)
            last_user_session = Session.get(and_(
                Session.updated == last_user_session_value,
                Session.user_id == user.id
                )
            )
            if (
                last_user_session
                and last_user_session.updated < delta
                and user.id not in user_ids
            ):
                user_ids.append(user.id)
                client.send_notification_to_pool(PushNotificationTemplate.REMINDER, user=session.user)

        print(f"{datetime.now(pytz.timezone('America/Mexico_City')).strftime('%d/%b/%Y %H:%M:%S')} {len(user_ids)} usuarios recordados")


def main():
    reminder = ReminderCrontab()
    reminder.remind_users_to_play()


if __name__ == '__main__':
    main()       

