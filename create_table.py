import sqlite3


class dbmodel:
    def __init__(self):
        self.conn = sqlite3.connect("database.db")
        print("connected succefully")

    def users(self):
        try:
            self.conn.execute(
                """
                 CREATE TABLE IF NOT EXISTS users(
                              id INTEGER PRIMARY KEY,
                              firstname VARCHAR,
                              surname  VARCHAR,
                              username VARCHAR,
                              email    VARCHAR,
                              password VARCHAR

                     )
               """
            )
            print("Created users table successfully")

        except:
            print(f"Error creating users table")

    def close(self):
        self.conn.close()


db_model = dbmodel()
db_model.users()
db_model.close()
