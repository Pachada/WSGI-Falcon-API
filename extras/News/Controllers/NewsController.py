from falcon.response import Response
from falcon.request import Request
from core.Controller import Controller, datetime, timedelta, json, HTTPStatus
from core.Utils import Utils
from models.News import News, and_
from models.User import User
from models.Person import Person
from core.classes.PushNotificationClient import PushNotificationClient
from models.PushNotificationTemplate import PushNotificationTemplate
import pytz


class NewsController(Controller):
    def on_get_pendings(self, req: Request, resp: Response):
        news = News.get_all(News.startdate >= datetime.utcnow())
        self.response(resp, HTTPStatus.OK, Utils.serialize_model(news))

    def on_get(self, req, resp, id=None):
        super().generic_on_get(req, resp, News, id, 
        filter =(and_(News.startdate <= datetime.utcnow(), News.enddate >= datetime.utcnow())),
        order_by=(News.startdate.desc())
        )

    def on_post(self, req: Request, resp: Response, id: int = None):
        if id:
            self.response(resp, HTTPStatus.METHOD_NOT_ALLOWED)
            return

        try:
            data: dict = json.loads(req.stream.read())

            startdate_utc, news_enddate = Utils.get_start_date_and_end_date(
                data.get("startdate"), 30
            )

            session = self.get_session(req, resp)
        if not session:
            return
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
                self.response(resp, HTTPStatus.INTERNAL_SERVER_ERROR, self.PROBLEM_SAVING_TO_DB)
                return

            # If the news has idType == 4 (Urgent), notified all the employees.
            # But when their stardate beggins
            if news.type_id == NewsType.URGENTE:

                users = User.get_all(and_(User.id != user.id))
                client = PushNotificationClient.get_instance()
                for user in users:
                    client.send_notification_to_pool(
                        user,
                        PushNotificationTemplate.URGENT_NEWS,
                        send_time=news.startdate,
                    )

            self.response(resp, HTTPStatus.CREATED, Utils.serialize_model(news))
            resp.append_header("content_location", f"/news/{news.id}")

        except Exception as exc:
            print(exc)
            self.response(resp, HTTPStatus.BAD_REQUEST, error=str(exc))

    def on_delete(self, req: Request, resp: Response, id=None):
        super().generic_on_delete(req, resp, News, id, soft_delete=False, delete_file=True)

    def on_put(self, req: Request, resp: Response, id: int = None):
        try:
            if not id:
                self.response(resp, HTTPStatus.METHOD_NOT_ALLOWED)
                return

            news = News.get(id)
            if not news:
                self.response(resp, HTTPStatus.NOT_FOUND, self.ID_NOT_FOUND)
                return

            data = json.loads(req.stream.read())
            self.set_values(news, data)
            news.save()

            data = Utils.serialize_model(news)
            self.response(resp, HTTPStatus.OK, data)

        except Exception as exc:
            print(exc)
            self.response(resp, HTTPStatus.BAD_REQUEST, error=str(exc))
