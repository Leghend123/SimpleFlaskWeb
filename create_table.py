import sqlite3

def create_users_table():
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                firstname VARCHAR,
                surname VARCHAR,
                username VARCHAR,
                email VARCHAR,
                password VARCHAR
            )
        """)

        conn.commit()
        conn.close()
        print("Created users table successfully")

    except Exception as e:
        print(f"Error creating users table: {e}")

# Call the function to create the users table
create_users_table()
