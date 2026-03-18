import sqlite3
import os
from enum import Enum

class Status(Enum):
    Reserved = 1
    In_Transit = 2
    Delievered = 3
    Recieved = 4

def connect():
    """Connects to the database in the Database folder
    returns the connetion
    """
    db_path = os.path.join(os.getcwd(),"Database",os.listdir(os.path.join(os.getcwd(),"Database"))[0])
    try:
        con = sqlite3.connect(db_path)
        print(f"Connected to {db_path} successfully.")
        return con
    except:
        print("Connection to database failed.")
        return None

def close_connection(con):
    """Closes the connection to the con
    """
    if con is not None:
        con.close()
        print("Connection to database closed.")
    else:
        print("No connection to database to close.")

def commit(con):
    """Commits the changes that has been done to the database(con)
    """
    if con is not None:
        con.commit()
        print("Changes committed to database.")
    else:
        print("No connection to database to commit changes.")

def execute_single_query(con,sql_insert_query):
    """Generic SQL execute
    """
    if con is not None:
        try:
            cursor = get_cursor(con)
            if len(sql_insert_query) == 2:
                cursor.execute(sql_insert_query[0],sql_insert_query[1])
            else:
                cursor.execute(sql_insert_query)
        except Exception as e:
            print(f"Error executing sql query: {sql_insert_query}, error: {e}")
    else:
        print("No connection to database")

def execute_multi_query(con,insert_sql):
    """Execute a list of SQL insert querys
    """
    if con is not None:
        try:
            for (insert,data) in insert_sql:
                execute_single_query(con,(insert,data))
        except Exception as e:
            print(f"Error getting table data: {e}")
            return 0
    else:
        print("No connection to database")
        return 0

def all_columns(con):
    """Gives the dict tables with their columns
    """
    c = get_cursor(con)
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in c.fetchall()]
    result = {}
    for tbl in tables:
        c.execute(f"PRAGMA table_info({tbl!r})")
        cols = [row[1] for row in c.fetchall()]
        result[tbl] = cols
    return result


# ----------------- GENERATE SQL STRINGS -----------------

def get_insert_cols(table,cols,data):
    """Logic for generating SQL insert query
    Generate specificly for all the columns of a specific table
    """
    try:
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
    except Exception as e:
        print(f"Error generating sql insert querey for cols: {e}")

    return(sql_full_string,col_data)

def get_insert(con, data):
    """Gets sql insert query for all the data
    Returns a tuple of the sql string and the specific column data
    """
    if con is not None:
        schema = all_columns(con)
        table_data = []

        for table, cols in schema.items():
            table_data.append(get_insert_cols(table,cols,data))
        
    return table_data

def update(con,table,column,column_value,primary_key, primary_key_id):
    """Updates the database(con) at the specific column with a specified value(colume_value)
    Only regarding the specific item(WHERE primary_key = primary_key_id)
    """
    if con is not None:
        try:
            cursor = get_cursor(con)
            cursor.execute(f"UPDATE {table} SET {column} = '{column_value}' WHERE {primary_key} = '{primary_key_id}'")
            commit(con)
        except Exception as e:
            print(f"Error updating: {e}")
    else:
        print("No connection to database while updating")
  
############## Deletion functions ##############        
def delete_all_data(con):
    cursor = get_cursor(con)
    schema = all_columns(con)
    for table, column in schema.items():
        cursor.execute(f"DELETE FROM {table}")
    commit(con)

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

# ----------------- GET -----------------

def get_cursor(con):
    """Gets the cursor of the con
    """
    if con is not None:
        return con.cursor()
    else:
        print("No connection to database.")
        return None

def get_table(con,table):
    """Gets the data from a specific table
    Returns all data conceerning the specific table
    """
    if con is not None:
        try:
            data = []
            cursor = get_cursor(con)
            cursor.execute(f"SELECT * FROM {table}")
            temp_data = cursor.fetchall()
            for d in temp_data:
                data.append(d[0])
        except Exception as e:
            print(f"Error getting table data: {e}")
            return 0
    else:
        print("No connection to database")
        return 0
    return data

def get_column(con,table,column):
    """Gets data from a specific table, from a specific column
    Returns all data concerning the specific column
    """
    if con is not None:
        try:
            data = []
            cursor = get_cursor(con)
            cursor.execute(f"SELECT {column} FROM {table}")
            temp_data = cursor.fetchall()
            for d in temp_data:
                data.append(d[0])
        except Exception as e:
            print(f"Error getting column data: {e}")
            return 0
    else:
        print("No connection to database")
        return 0
    return data

def get_id(con,table,column,id):
    """Gets data from specific table, from specific column, with specific id
    Returns all data concerning the specific id
    """
    if con is not None:
        try:
            data = []
            cursor = get_cursor(con)
            cursor.execute(f"SELECT * FROM {table} WHERE {column} = '{id}'")
            temp_data = cursor.fetchall()
            for d in temp_data:
                data.append(d)
        except Exception as e:
            print(f"Error getting id data: {e}")
            return 0
    else:
        print("No connection to database")
        return 0
    return data


def get_all_data(con):
    """Gets entire dataset from database
    """
    if con is not None:
        try:
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
        except Exception as e:
            print(f"Error getting all data: {e}")
            return 0
    else:
        print("No connection to database")
        return 0
    return total

def get_tables_and_columns(schema):
    """Gets tables and columns from schema
    Returns a list of tables and a dict of columns
    """
    if schema is not None:
        try:
            tables = []
            columns = {}
            for table, column in schema.items():
                tables.append(table)
                columns[table] = column
        except Exception as e:
            print(f"Error extracting tables and columns: {e}")
            return 0
    else:
        print("No Schema given")
        return 0
    return tables, columns

def get_column_data_type(con, table, column):
    """Gets the specific datatype of a column in a table
    """
    if con is not None:
        try:
            c = get_cursor(con)
            c.execute(f"PRAGMA table_info({table!r})")
            cols = c.fetchall()
            for col in cols:
                if col[1] == column:
                    return col[2]
        except Exception as e:
            print(f"Error getting column datatype: {e}")
    else:
        print("No connection to database")
    
def get_datatypes(con,table,columns): 
    """Get datatypes for all columns in a table
        Returns dict of columns with their datatype
    """
    if con is not None:
        try:
            datatypes = {}
            for column in columns:
                datatypes[column] = get_column_data_type(con,table,column)
        except Exception as e:
            print(f"Error getting datatypes: {e}")
            return 0
    else:
        print("No connection to database")
        return 0
    return datatypes

def get_primary_key(con, table):
    """Gets the primary key column (name) of a table
    """
    if con is not None:
        try:
            cursor = get_cursor(con)
            cursor.execute(f"PRAGMA table_info({table})")
            for row in cursor.fetchall():
                if row[5] == 1: # PK column has 1 in the 6th position of the PRAGMA output
                    return row[1]
        except Exception as e:
            print(f"Error getting primary key: {e}")
            return 0
    else:
        print("No connection to database")
        return 0
    return "ID"
 
def get_connected_tables(con, parent_table): # Find tables that have a foreign key referencing the parent_table
    if con is not None:
        try:
            schema = all_columns(con)
            reference = []
            for table, columns in schema.items():
                cursor = get_cursor(con)
                cursor.execute(f"PRAGMA foreign_key_list({table})")
                for row in cursor.fetchall():
                    if row[2] == parent_table:
                        reference.append((table, row[3], row[4])) # row[3] is the column in the child table that references the parent table, row[4] is the column in the parent table that is referenced
        except Exception as e:
            print(f"Error getting connected tables: {e}")
            return 0
    else:
        print("No connection to database")
        return 0
    return reference
 
def get_mathing_ids(con, table, col, val):
    if con is not None:
        try:
            cursor = get_cursor(con)
            pk_column = get_primary_key(con, table)
            cursor.execute(f"SELECT {pk_column} FROM {table} WHERE {col} = ?", (val,))
            ids = [row[0] for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error getting matching ids: {e}")
            return 0
    else:
        print("No connection to database")
        return 0
    return ids, pk_column

# ----------------- RESERVED DATABASE -----------------

def connect_reserved_db():
    """Connects to the reserved Database
    """
    try:
        con = sqlite3.connect(os.path.join(os.getcwd(),"Reserved","Reserved.db"))
        print("Connected to database successfully.")
        return con
    except:
        print("Connection to database failed.")
        return None
    
def create_transit_table(con,prim_key,data_type):
    """Creates the Transit Table in the database
    """
    if con is not None:
        try:
            execute_single_query(con,f"""CREATE TABLE IF NOT EXISTS Transit_Table (
                {prim_key} {data_type} PRIMARY KEY,
                Status TEXT NOT NULL,
                Quantity INTEGER NOT NULL,
                From_Location TEXT NOT NULL,
                To_Location TEXT NOT NULL);""")
            commit(con)
        except Exception as e:
            print(f"Error creating Transit Table: {e}")
            return 0
    else:
        print("No connection to database")
        return 0

def insert_transit_table(con,data):
    """Inserts the data into the Transit Table
    """
    if con is not None:
        try: 
            schema = all_columns(con)
            for table,columns in schema.items():
                if table == "Transit_Table":
                    execute_single_query(con,get_insert_cols(table,columns,data))
        except Exception as e:
            print(f"Error insert Transit Table data: {e}")
            return 0
    else:
        print("No connection to database")
        return 0
    return 1

def update_transit(con,status,primary_key, primary_key_id):
    """Updates the status of the Transit Table
    """
    if con is not None:
        try:
            for s in Status:
                if s.value == status:
                    update(con, "Transit_Table", "Status", s.name, primary_key, primary_key_id)
                    return 1
        except Exception as e:
            print(f"Error updating Transit Table Status: {e}")
            return 0
    else:
        print("No connection to database")
        return 0

def initiate_reserved_data(prim_key,prim_key_val,quantity,from_loc,to_loc):
    """Generates the initial data for the Transit Table
    """
    data = {};data[prim_key] = prim_key_val;data["Status"] = "Reserved"
    data["Quantity"] = quantity;data["From_Location"] = from_loc
    data["To_Location"] = to_loc
    return data

def reserve_data(con,prim_key,prim_key_val,quantity,from_loc,to_loc):
    """Reserves the data
    Done by generating and inserting into the Transit Table
    """
    if con is not None:
        try: 
            data = initiate_reserved_data(prim_key,prim_key_val,quantity,from_loc,to_loc)

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
        except Exception as e:
            print(f"Error reserving data: {e}")
            return 0
    else:
        print("No connection to database")
        return 0
