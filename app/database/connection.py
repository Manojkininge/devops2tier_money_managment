import mysql.connector

from app.config.config import Config


class DatabaseConnection:

    def __init__(self):
        self.connection = None

    def connect(self):
        self.connection = mysql.connector.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )

        return self.connection

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            self.connection = None
