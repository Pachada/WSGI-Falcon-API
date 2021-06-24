from core.Controller import Controller, datetime, timedelta, json
from core.Utils import Utils
from models.News import News
from models.User import User
from models.Employee import Employee
from models.Person import Person
from core.classes.PushNotificationClient import PushNotificationClient
from models.PushNotificationTemplate import PushNotificationTemplate
import pytz

class NewsController(Controller):

    def on_get_pendings(self, req, resp):
        news = News.getAll(News.startdate >= datetime.utcnow())
        self.response(resp, 200, Utils.serializeModel(news))

    def on_get(self, req, resp, id=None):
        if id:
            news = News.get(id)
            if not news:
                self.response(resp, 404, self.ID_NOT_FOUND)
                return
        else:        
            today = datetime.utcnow()

            news = News.getAll(
                and_(
                    News.startdate <= today,
                    News.enddate >= today
                ),
                orderBy=News.startdate.desc()
                )
            
        self.response(resp, 200, Utils.serializeModel(news))
    

    def on_post(self, req, resp, id=None):
        if id:
            self.response(resp, 405)
            return

        try:
            data:dict = json.loads(req.stream.read())

            if not data.get('startdate') is not None:
                startdate_utc = datetime.utcnow()

            else:
                startdate_formated = datetime.strptime(data.get('startdate'), "%Y-%m-%dT%H:%M:%S")
                # Transfor the datetime object with time zone America/Mexico_City to UTC0 
                local_timezone = pytz.timezone("America/Mexico_City")
                local_startdate = local_timezone.localize(startdate_formated)
                startdate_utc = local_startdate.astimezone(pytz.utc)

                # If it only has the date but not hours and if it is the same day as today: the stardate is utcnow.
                # if it has date but not hours and is a different day as today: the startdate is the one sended.
                # if it has date and hour the stardate is the one sended
                today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                if startdate_formated.hour == 0 and startdate_formated.minute == 0 and startdate_formated.second == 0:
                    if today == startdate_formated:
                        startdate_utc = datetime.utcnow()

            # A new is only availabe for 30 days
            news_enddate = startdate_utc + timedelta(days=30)

            session = req.context.session
            client = session.client
            user:User = session.user

            news = News(
                idClient = client.id, 
                idUser = user.id,
                idFile = data.get('idFile', None),
                idThumbnail=data.get('idThumbnail', None),
                idType = data.get('type'), 
                title = data.get('title'),
                body = data.get('body'),
                startdate = startdate_utc,
                enddate = news_enddate
                )

            if not news.save():
                self.response(resp,500,self.PROBLEM_SAVING_TO_DB)
                return
            
            # If the news has idType == 4 (Urgent), notified all the employees.
            # But when their stardate beggins
            if news.idType == 4:
                
                employees = Employee.getAll(and_(
                    Employee.idClient == user.idClient,
                    Employee.idUser != user.id
                    ))
                client = PushNotificationClient.get_instance()
                person:Person = user.person
                data_for_notification = {"user_who_created": f'{person.firstname} {person.lastname}'}
                for employee in employees:
                    client.send_notification_to_pool(employee, PushNotificationTemplate.URGENT_NEWS, data_for_notification, notification_time=news.startdate)

            self.response(resp, 201, Utils.serializeModel(news))
            resp.append_header('content_location', f"/news/{news.id}")

        except Exception as exc:
            print(exc)
            self.response(resp, 400, error = str(exc))

    def on_delete(self, req, resp, id=None):
        if not id:
            self.response(resp,405)
            return

        news = News.get(id)
        if not news:
            self.response(resp,404,self.ID_NOT_FOUND)
            return

        news.soft_delete()
        news.save()

        # check if someone different from the original creaton delete it
        user: User = req.context.session.user
        if (news.idUser != user.id):
            # send notification to origianl creator
            client = PushNotificationClient.get_instance()
            employee = Employee.get(Employee.idUser == news.idUser)
            person:Person = user.person
            notification_data = {"user_who_deleted": f"{person.firstname} {person.lastname}"}
            client.send_notification_to_pool(employee, PushNotificationTemplate.DELETED_NEWS, notification_data)

        self.response(resp, 200, Utils.serializeModel(news))

    def on_put(self, req, resp, id=None):
        try:
            if not id:
                self.response(resp, 405)
                return

            news = News.get(id)
            if not news:
                self.response(resp,404,self.ID_NOT_FOUND)
                return

            data = json.loads(req.stream.read())
            self.set_values(news, data)
            news.save()
            # check if someone different from the original creaton update it
            user: User = req.context.session.user
            if (news.idUser != user.id):
                # send notification to origianl creator
                client = PushNotificationClient.get_instance()
                employee = Employee.get(Employee.idUser == news.idUser)
                person:Person = user.person
                notification_data = {"user_who_edited": f"{person.firstname} {person.lastname}"}
                client.send_notification_to_pool(employee, PushNotificationTemplate.MODIFIED_NEWS, notification_data)

            data = Utils.serializeModel(news)
            self.response(resp,200,data)

        except Exception as exc:
            print(exc)
            self.response(resp, 400, error = str(exc))
