import sqlite3

data_base = "LetMilk.db"

def connect():
    try:
        con = sqlite3.connect(data_base)
        print("Connected to database successfully.")
        return con
    except:
        print("Connection to database failed.")
        return None

def close_connection(con):
    if con is not None:
        con.close()
        print("Connection to database closed.")
    else:
        print("No connection to database to close.")

def get_cursor(con):
    if con is not None:
        return con.cursor()
    else:
        print("No connection to database.")
        return None

def commit(con):
    if con is not None:
        con.commit()
        print("Changes committed to database.")
    else:
        print("No connection to database to commit changes.")

def create_table(con, create_table_sql):
    if con is not None:
        try:
            c = get_cursor(con)
            c.execute(create_table_sql)
            print("Table created successfully.")
        except Exception as e:
            print(f"Error creating table: {e}")
    else:
        print("No connection to database to create table.")

def insert_table(con, insert_sql, data):
    if con is not None:
        try:
            c = get_cursor(con)
            c.execute(insert_sql, data)
            print("Data inserted successfully.")
        except Exception as e:
            print(f"Error inserting data: {e}")
    else:
        print("No connection to database to insert data.")