from datetime import datetime

import psycopg2 as ps

from database.config import host, user, password, db_name, schema_name


class DataBase:
    def __init__(self):
        self.connection = ps.connect(
                host=host,
                user=user,
                password=password,
                database=db_name
            )
        self.connection.autocommit = True

    # Выполнение SQL-запроса
    def exec_update_query(self, query):

        with self.connection.cursor() as cursor:
            # Выполняем SQL-запрос
            cursor.execute(query)

        # Выполнение SQL-запроса с возвратом данных (для SELECT)

    def exec_query(self, query):
        with self.connection.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()

    def save_order_date(self, tg_id, dates):
        #query = "INSERT INTO orders (tg_id, date) VALUES (%s, %s)"
        date_list = dates.split()

        for date_str in date_list:
            try:
                # Проверяем дату и приводим к нужному формату
                date_obj = datetime.strptime(f"{date_str}.2025", "%d.%m.%Y")
                formatted_date = date_obj.strftime("%d.%m.%Y")

                # Сохраняем в БД
                self.exec_update_query(f"INSERT INTO orders (tg_id, date) VALUES ('{tg_id}', '{formatted_date}')")
            except ValueError:
                print(f"Ошибка: некорректная дата {date_str}")

    def save_user_action(self, tg_id, tg_username, action):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        query = f"""
        INSERT INTO user_actions (tg_id, tg_username, timestamp, action)
        VALUES ('{tg_id}', '{tg_username}', '{timestamp}', '{action}')
        """

        self.exec_update_query(query)

    def save_poll_answer(self, tg_id, answer):
        query = f"SELECT 1 FROM survey WHERE tg_id = {tg_id}"
        result = self.exec_query(query)

        if result:
            return False

        query = f"INSERT INTO survey (tg_id, answer) VALUES ('{tg_id}', '{answer}')"
        self.exec_update_query(query)
        return True