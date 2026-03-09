import sqlite3

data_base = "LetMilk.db"

def connect():
    try:
        conn = sqlite3.connect(data_base)
        print("Connected to database successfully.")
        return conn
    except:
        print("Connection to database failed.")
        return None

def close_connection(conn):
    if conn is not None:
        conn.close()
        print("Connection to database closed.")
    else:
        print("No connection to database to close.")

def get_cursor(conn):
    if conn is not None:
        return conn.cursor()
    else:
        print("No connection to database.")
        return None

def commit(conn):
    if conn is not None:
        conn.commit()
        print("Changes committed to database.")
    else:
        print("No connection to database to commit changes.")

def create_table(conn, create_table_sql):
    if conn is not None:
        try:
            c = conn.cursor()
            c.execute(create_table_sql)
            print("Table created successfully.")
        except Exception as e:
            print(f"Error creating table: {e}")
    else:
        print("No connection to database to create table.")

def insert_table(conn, insert_sql, data):
    if conn is not None:
        try:
            c = conn.cursor()
            c.execute(insert_sql, data)
            print("Data inserted successfully.")
        except Exception as e:
            print(f"Error inserting data: {e}")
    else:
        print("No connection to database to insert data.")