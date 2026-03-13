import sqlite3

def connect():
    try:
        con = sqlite3.connect("LetMilk.db")
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

def all_columns(con):
    c = get_cursor(con)
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in c.fetchall()]
    result = {}
    for tbl in tables:
        c.execute(f"PRAGMA table_info({tbl!r})")
        cols = [row[1] for row in c.fetchall()]
        result[tbl] = cols
    return result

def get_tables_and_columns(schema):
    tables = []
    columns = {}
    for table, column in schema.items():
        tables.append(table)
        columns[table] = column
    return tables, columns

def insert_data(con,insert_sql):
    if con is not None:
        try:
            c = get_cursor(con)
            for (insert,data) in insert_sql:
                c.execute(insert,data)
            print("All data inserted")
        except Exception as e:
            print(f"Error inserting data: {e}")
    else:
        print("No connection to database to insert data.")

def get_insert(con, data):
    schema = all_columns(con)
    table_data = []

    for table, cols in schema.items():
        sql_string = []
        col_data = []
        sql_full_string = ""

        sql_string.append(f"INSERT INTO {table} (")

        for col in cols[:-1]:
            sql_string.append(f"{col},")
            col_data.append(data[col])
        sql_string.append(f"{cols[-1]}")
        col_data.append(data[cols[-1]])
        
        sql_string.append(f") VALUES ({"?, " * (len(cols)-1)}?);")
        for string in sql_string:
            sql_full_string += str(string)

        table_data.append((sql_full_string,col_data))
    
    return table_data

def get_all_data(con):
    total = {}
    cursor = get_cursor(con)
    schema = all_columns(con)
    for table, column in schema.items():
        for item in column:
            cursor.execute(f"SELECT {item} FROM {table}")
            data = cursor.fetchall()
            cur_data = []
            for i in data:
                cur_data.append(i[0])
            total[item] = cur_data
    return total

def get_table(con,table):
    data = []
    cursor = get_cursor(con)
    cursor.execute(f"SELECT * FROM {table}")
    temp_data = cursor.fetchall()
    for d in temp_data:
        data.append(d[0])
    return data

def get_column(con,table,column):
    data = []
    cursor = get_cursor(con)
    cursor.execute(f"SELECT {column} FROM {table}")
    temp_data = cursor.fetchall()
    for d in temp_data:
        data.append(d[0])
    return data

def get_id(con,table,column,id):
    data = []
    cursor = get_cursor(con)
    cursor.execute(f"SELECT * FROM {table} WHERE {column} = '{id}'")
    temp_data = cursor.fetchall()
    for d in temp_data:
        data.append(d)
    return data
