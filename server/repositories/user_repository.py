import sqlite3
import repositories.constants as C
from factories.user_factory import UserFactory


class UserRepository:

    def __init__(self):
        self.user_factory = UserFactory()

    def create_tables(self):
        db = sqlite3.connect(C.DB_NAME)
        cursor = db.cursor()
        cursor.executescript(C.CREATE_TABLES_QUERY)
        db.close()

    def create(self, username, ip, port):
        db = sqlite3.connect(C.DB_NAME)
        cursor = db.cursor()
        cursor.execute(C.INSERT_QUERY, (username, ip, port))
        id = cursor.lastrowid
        db.commit()
        db.close()
        return id

    def get_by_ip(self, ip):
        db = sqlite3.connect(C.DB_NAME)
        cursor = db.cursor()
        cursor.execute(C.SELECT_BY_IP_QUERY, (ip,))
        user = cursor.fetchone()
        db.close()
        if user is None:
            return user
        return self.user_factory.create_from_tuple(user)
