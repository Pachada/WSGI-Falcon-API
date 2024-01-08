from models.Status import Status, and_, datetime, Model, Utils


class NotificationCronsUtils:

    max_send_attempts = 3

    def main(self, limit):
        # Implemented in subclass
        raise NotImplementedError

    def procces_pool(self, limit: int = 10):
        """Start the sending procces"""
        self.main(limit)

    def get_rows_to_send(self, model: Model, query_limit):
        return model.get_all(
            and_(
                model.status_id.in_([Status.PENDING, Status.ERROR]),
                model.send_time <= datetime.utcnow()
            ),
            limit=query_limit,
        )

    def put_rows_in_proccesing_status(self, data: list):
        for row in data:
            row.status_id = Status.PROCESSING

        Model.save_all(data)

    def row_with_errors(self, row: Model):
        row.send_attemps += 1
        if row.send_attemps >= self.max_send_attempts:
            row.delete()
            return

        row.status_id = Status.ERROR
        row.save()

    def show_results(self, selected: int, errors: int):
        send = selected - errors
        print(
            f'Date and time: {Utils.today_in_tz().strftime("%d/%b/%Y %H:%M:%S")}, selected: {selected}, sended: {send}, errores: {errors}'
        )

    def nothing_to_send(self):
        print(f'Date and time: {Utils.today_in_tz().strftime("%d/%b/%Y %H:%M:%S")}, nothing to send')
