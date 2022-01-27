from models.User import User, datetime
from models.SmsPool import SmsPool, SmsTemplate
from crons.SmsCrontab import SmsCrontab


class SmsClient:
    
    @staticmethod
    def send_sms_to_pool(
        template_id: int,
        user, # type:  User | list
        data: dict = {},
        send_time: datetime = datetime.utcnow(),
        send_now=False
    ):
        """
        Gives format to the message to send and save it to the sms pool.

        Parameters
        ----------
        template_id  :  `int`
                id of the SmsTemplate.
        user  :  `None`,`User`,`list`
                A User or a list of Users to send the push to.
                None if the target is all users.
        data  :  `dict`
                The data to be replace in the SmsTemplate.
        send_time  :  `datetime`
                The UTC time to send the sms, utcnow() by default.
        send_now  :  `bool`
                If the sms should be process/sended right away.
                False by default.
                
        Returns
        ----------
        `None`
        """
        template = SmsTemplate.get(template_id)
        message = SmsClient.__format_message(template, data)

        if isinstance(user, list):
            for item in user:
                SmsClient.__save_to_pool(template, message, send_time, item)
            return

        SmsClient.__save_to_pool(template, message, send_time, user)

        if send_now and send_time <= datetime.utcnow():
            client = SmsCrontab.get_instance() 
            client.procces_pool()

    @staticmethod
    def __format_message(template: SmsTemplate, data: dict):
        message = template.message
        for key in data:
            message = message.replace(
                "{{" + key + "}}", data[key]
            )
        
        return message
    
    @staticmethod
    def __save_to_pool(
        template: SmsTemplate, 
        message: str,
        send_time: datetime,
        user: User 
        ):
        sms = SmsPool(
            user_id=user.id,
            template_id=template.id,
            message=message,
            send_time=send_time
        )
        
        sms.save()
