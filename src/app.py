import database_commands as db
from flask import Flask, render_template, jsonify
from flask_restx import Api, Namespace, Resource, fields, Model
import os

app = Flask(__name__)

''' Create the homepage for the API, which will display all the tables and columns in the database, as well as all the data in the database. '''
@app.route("/")
def home():
    con = db.connect()
    tables, columns = db.get_tables_and_columns(db.all_columns(con))
    total_data = db.get_all_data(con)
    column_data_types = {}
    for table in tables:
        for column in columns[table]:
            ''' Get the data type of the column, and create a model field for it.'''
            data_type = db.get_column_data_type(con, table, column)
            input_type = ""
            match data_type:
                case "INTEGER":
                    input_type = "number"
                case "REAL":
                    input_type = "number"
                case "TEXT":
                    input_type = "text"
                case "TIMESTAMP":
                    input_type = "datetime-local"
            column_data_types[(table, column)] = input_type
    db.close_connection(con)
    return render_template("index.html")#, tables=tables, columns=columns, total_data=total_data, column_data_types=column_data_types)

@app.route("/api/tables", methods=["GET"])
def get_tables():
    con = db.connect()
    tables, columns = db.get_tables_and_columns(db.all_columns(con))
    return jsonify(tables)

@app.route("/api/columns", methods=["GET"])
def get_columns():
    con = db.connect()
    tables, columns = db.get_tables_and_columns(db.all_columns(con))
    return jsonify(columns)

@app.route("/api/column_types", methods=["GET"])
def get_column_types():
    con = db.connect()
    tables, columns = db.get_tables_and_columns(db.all_columns(con))
    column_data_types = {}
    for table in tables:
        for column in columns[table]:
            ''' Get the data type of the column, and create a model field for it.'''
            data_type = db.get_column_data_type(con, table, column)
            input_type = ""
            match data_type:
                case "INTEGER":
                    input_type = "number"
                case "REAL":
                    input_type = "number"
                case "TEXT":
                    input_type = "text"
                case "TIMESTAMP":
                    input_type = "datetime-local"
            column_data_types[(table, column)] = input_type
    return jsonify(column_data_types)

''' Create the API to handle docs and all the endpoints for the API.'''
api = Api(
    app,
    title="Best Storage System Ever API",
    version="1.0",
    description="API for the best storage system ever",
    doc="/docs"
)

def get_table(self):
    ''' Get all items from the table in the database, and return them as a JSON object.'''
    table = self.table
    conn = db.connect()
    data = db.get_table(conn, table)
    db.close_connection(conn)
    return data

def post_item(self):
    ''' Create a new item with the specified ID in the table in the database, and return it as a JSON object.'''
    table = self.table
    data = api.payload
    conn = db.connect()
    db.execute_single_query(conn, db.get_insert_cols(con=conn, table_id=table, data=data))
    db.commit(conn)
    db.close_connection(conn)
    return 201

def delete_table(self):
    ''' Delete all items from the table in the database, and return a success message.'''
    table = self.table
    conn = db.connect()
    db.delete_table_data(conn, table)
    db.close_connection(conn)
    return 201

def get_item(self, id):
    ''' Get a single item with the specified ID from the table in the database, and return it as a JSON object.'''
    table = self.table
    conn = db.connect()
    column = db.get_primary_key(conn, table)
    data = db.get_id(conn, table, column, id)
    db.close_connection(conn)
    return data

def put(self, id):
    ''' Update a single item with the specified ID in the table in the database, and return it as a JSON object.'''
    table = self.table
    data = api.payload
    conn = db.connect()
    db.put(conn, table_id=table, pk_id=id, data=data)
    db.close_connection(conn)
    return 201

def delete_item(self, id):
    ''' Delete a single item with the specified ID from the table in the database, and return a success message.'''
    table = self.table
    conn = db.connect()
    column = db.get_primary_key(conn, table)
    db.delete_id(conn, table, column, id)
    db.close_connection(conn)
    return 201

def create_resource(table_name, namespace: Namespace, model_fields):
    model = namespace.model(f"{table_name}", model_fields)
    table_attrs = {
        "table": table_name,
    }
    table_attrs["get"] = namespace.marshal_list_with(model)(get_table)
    table_attrs["delete"] = namespace.marshal_with(model)(delete_table)
    table_attrs["post"] = namespace.expect(model)(post_item)
    table_attrs["post"] = namespace.marshal_with(model)(post_item)
    TableResourceClass = type(f"{table_name}", (Resource,), table_attrs)

    prim_key_attrs = {
        "table": table_name,
    }
    prim_key_attrs["get"] = namespace.marshal_list_with(model)(get_item)
    prim_key_attrs["delete"] = namespace.marshal_with(model)(delete_item)
    prim_key_attrs["put"] = namespace.expect(model)(put)
    prim_key_attrs["put"] = namespace.marshal_list_with(model)(put)
    PrimKeyResourceClass = type("Primary_Key", (Resource,), prim_key_attrs)
    
    return TableResourceClass, PrimKeyResourceClass

''' Create the API documentation for all the tables and columns in the database.'''
def create_api_and_docs():
    con = db.connect()
    tables, columns = db.get_tables_and_columns(db.all_columns(con))
    namespaces_and_models = []
    for table in tables:
        ''' Create a namespace for each table in the database, and create a model for each column in the table.'''
        namespace = Namespace(table, description=f"Operations related to {table} in the storage system")
        primary_key = db.get_primary_key(con, table)
        primary_key_type = ""
        model_fields = {}
        for column in columns[table]:
            ''' Get the data type of the column, and create a model field for it.'''
            data_type = db.get_column_data_type(con, table, column)
            model = ""
            match data_type:
                case "INTEGER":
                    if column == primary_key:
                        primary_key_type = "int"
                    model = fields.Integer(required=True, description=f"{column} of {table}")
                case "REAL":
                    if column == primary_key:
                        primary_key_type = "float"
                    model = fields.Float(required=True, description=f"{column} of {table}")
                    
                case "TEXT":
                    if column == primary_key:
                        primary_key_type = "string"
                    model = fields.String(required=True, description=f"{column} of {table}")
            
            model_fields[column] = model
        
        namespaces_and_models.append((namespace, model_fields, table, primary_key_type))
    
    db.close_connection(con)

    for namespace, model_fields, table, primary_key_type in namespaces_and_models:
        ''' Create the endpoints for each table in the database, and use the model to validate the input data.'''
        TableResource, PrimKeyResource = create_resource(table_name=table, namespace=namespace, model_fields=model_fields)

        namespace.add_resource(TableResource, f"/")
        namespace.add_resource(PrimKeyResource, f"/<{primary_key_type}:id>")

        api.add_namespace(namespace)        

''' Call the function to create the API methods for all the tables and columns in the database.'''
#create_api_methods()
''' Call the function to create the API documentation for all the tables and columns in the database.'''
create_api_and_docs()


if __name__ == "__main__":
    app.run(debug=True)
    
