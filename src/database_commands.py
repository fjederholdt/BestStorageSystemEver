import sqlite3
import os

def connect():
    db_path = os.path.join(os.getcwd(),"Database",os.listdir(os.path.join(os.getcwd(),"Database"))[0])
    try:
        con = sqlite3.connect(db_path)
        print(f"Connected to {db_path} successfully.")
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
            commit(con)
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

def get_column_data_type(con, table, column):
    c = get_cursor(con)
    c.execute(f"PRAGMA table_info({table!r})")
    cols = c.fetchall()
    for col in cols:
        if col[1] == column:
            return col[2]
    
def insert_data(con,insert_sql):
    if con is not None:
        try:
            c = get_cursor(con)
            for (insert,data) in insert_sql:
                c.execute(insert,data)
            print("All data inserted")
            return True
        except Exception as e:
            print(f"Error inserting data: {e}")
            return False
    else:
        print("No connection to database to insert data.")
        return False

def get_insert_cols(table,cols,data):
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

    return(sql_full_string,col_data)

def get_insert(con, data):
    schema = all_columns(con)
    table_data = []

    for table, cols in schema.items():
        table_data.append(get_insert_cols(table,cols,data))
    
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
  
############## Deletion functions ##############        
def delete_all_data(con):
    cursor = get_cursor(con)
    schema = all_columns(con)
    for table, column in schema.items():
        cursor.execute(f"DELETE FROM {table}")
    commit(con)
        
def get_primary_key(con, table):
    cursor = get_cursor(con)
    cursor.execute(f"PRAGMA table_info({table})")
    for row in cursor.fetchall():
        if row[5] == 1: # PK column has 1 in the 6th position of the PRAGMA output
            return row[1]
    return "ID"
 
def get_connected_tables(con, parent_table): # Find tables that have a foreign key referencing the parent_table
    schema = all_columns(con)
    reference = []
    for table, columns in schema.items():
        cursor = get_cursor(con)
        cursor.execute(f"PRAGMA foreign_key_list({table})")
        for row in cursor.fetchall():
            if row[2] == parent_table:
                reference.append((table, row[3], row[4])) # row[3] is the column in the child table that references the parent table, row[4] is the column in the parent table that is referenced
       
    return reference
 
def get_mathing_ids(con, table, col, val):
    cursor = get_cursor(con)
    pk_column = get_primary_key(con, table)
    cursor.execute(f"SELECT {pk_column} FROM {table} WHERE {col} = ?", (val,))
    ids = [row[0] for row in cursor.fetchall()]
    return ids, pk_column

# how to delete by column value with cascade delete across all related tables, works for any DBc
def delete_by_column(con, table, col, val, _visited=None):
    if _visited is None:
        _visited = set() # to avoid infinite recursion in case of circular references
    visit_key = (table, col, str(val))
    if visit_key in _visited:
        return
    _visited.add(visit_key)
#    # Find all tables that reference this table

    references = get_connected_tables(con, table)   
    for ref_table, ref_col, parent_col in references:
        # Find matching IDs in the parent table
        ids, pk_column = get_mathing_ids(con, table, col, val)
        if not ids:
            continue
        # For each matching ID, delete from the referencing table
        for id in ids:
            delete_by_column(con, ref_table, ref_col, id, _visited) # recursive call to delete from child tables
    # Finally, delete from the original table
    cursor = get_cursor(con)
    cursor.execute(f"DELETE FROM {table} WHERE {col} = ?", (val,))
    commit(con)


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
  
def update(con,table,column,val,col_id,val_id):
    if con is not None:
        try:
            cursor = get_cursor(con)
            cursor.execute(f"UPDATE {table} SET {column} = {val} where {col_id} = {val_id}")
            commit(con)
        except Exception as e:
            print(f"Error updating: {e}")
    else:
        print("No connection to database while updating")

def connect_reserved_db():
    try:
        con = sqlite3.connect(os.path.join(os.getcwd(),"Reserved","Reserved.db"))
        print("Connected to database successfully.")
        return con
    except:
        print("Connection to database failed.")
        return None
    
def create_transit_table(con,prim_key,data_type):
    create_table(con,f"""CREATE TABLE IF NOT EXISTS Transit_Table (
        {prim_key} {data_type} PRIMARY KEY,
        Status TEXT NOT NULL,
        Quantity INTEGER NOT NULL,
        From_Location TEXT NOT NULL,
        To_Location TEXT NOT NULL
                                    );""")
    commit(con)

def insert_transit_table(con,data):
    schema = all_columns(con)
    for table,columns in schema.items():
        if table == "Transit_Table":
            (sql, col_data) = get_insert_cols(table,columns,data)
            insert_table(con,sql,col_data)
    return 1

def get_datatypes(con,table,columns):
    datatypes = {}
    for column in columns:
        datatypes[column] = get_column_data_type(con,table,column)
    return datatypes

def initiate_reserved_data(prim_key,prim_key_val,quantity,from_loc,to_loc):
    data = {};data[prim_key] = prim_key_val;data["Status"] = "Reserved"
    data["Quantity"] = quantity;data["From_Location"] = from_loc
    data["To_Location"] = to_loc
    return data

def reserve_data(con,prim_key,prim_key_val,quantity,from_loc,to_loc):
    data = initiate_reserved_data(prim_key,prim_key_val,quantity,from_loc,to_loc)

    #Make sure someone does the put call to update the quantity, Does this has to be done from gui?!?!?!
    if type(prim_key_val) is int:
        data_type = "INTEGER"
    elif type(prim_key_val) is str:
        data_type = "TEXT"
    elif type(prim_key_val) is float:
        data_type = "REAL"
    else:
        print("No datatype")
        quit()

    create_transit_table(con,prim_key,data_type)
    insert_transit_table(con,data)

