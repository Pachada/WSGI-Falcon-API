from falcon.response import Response
from falcon.request import Request
from core.Controller import Controller, datetime, timedelta, json
from core.Utils import Utils
from models.News import News, and_
from models.User import User
from models.Person import Person
from core.classes.PushNotificationClient import PushNotificationClient
from models.PushNotificationTemplate import PushNotificationTemplate
import pytz


class NewsController(Controller):
    def on_get_pendings(self, req: Request, resp: Response):
        news = News.getAll(News.startdate >= datetime.utcnow())
        self.response(resp, 200, Utils.serialize_model(news))

    def on_get(self, req, resp, id=None):
        super().generic_on_get(req, resp, News, id, 
        filter =(and_(News.startdate <= datetime.utcnow(), News.enddate >= datetime.utcnow())),
        orderBy=(News.startdate.desc())
        )

    def on_post(self, req: Request, resp: Response, id: int = None):
        if id:
            self.response(resp, 405)
            return

        try:
            data: dict = json.loads(req.stream.read())

            startdate_utc, news_enddate = Utils.get_start_date_and_end_date(
                data.get("startdate"), 30
            )

            session = req.context.session
            user: User = session.user

            news = News(
                user_id=user.id,
                file_id_image=data.get("file_id"),
                file_id_thumbnail=data.get("thumbnail_id"),
                type_id=data.get("type"),
                title=data.get("title"),
                body=data.get("body"),
                startdate=startdate_utc,
                enddate=news_enddate,
            )


            if not news.save():
                self.response(resp, 500, self.PROBLEM_SAVING_TO_DB)
                return

            # If the news has idType == 4 (Urgent), notified all the employees.
            # But when their stardate beggins
            if news.type_id == NewsType.URGENTE:

                users = User.getAll(and_(User.id != user.id))
                client = PushNotificationClient.get_instance()
                for user in users:
                    client.send_notification_to_pool(
                        user,
                        PushNotificationTemplate.URGENT_NEWS,
                        notification_time=news.startdate,
                    )

            self.response(resp, 201, Utils.serialize_model(news))
            resp.append_header("content_location", f"/news/{news.id}")

        except Exception as exc:
            print(exc)
            self.response(resp, 400, error=str(exc))

    def on_delete(self, req: Request, resp: Response, id=None):
        super().generic_on_delete(req, resp, News, id, soft_delete=False, delete_file=True)

    def on_put(self, req: Request, resp: Response, id: int = None):
        try:
            if not id:
                self.response(resp, 405)
                return

            news = News.get(id)
            if not news:
                self.response(resp, 404, self.ID_NOT_FOUND)
                return

            data = json.loads(req.stream.read())
            self.set_values(news, data)
            news.save()

            data = Utils.serialize_model(news)
            self.response(resp, 200, data)

        except Exception as exc:
            print(exc)
            self.response(resp, 400, error=str(exc))
