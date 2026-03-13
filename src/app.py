from unittest import case

import database_commands as db
from flask import Flask, render_template
from flask_restx import Api, Resource, fields

app = Flask(__name__)

''' Create the homepage for the API, which will display all the tables and columns in the database, as well as all the data in the database. '''
@app.route("/")
def home():
    con = db.connect()
    tables, columns = db.get_tables_and_columns(db.all_columns(con))
    total_data = db.get_all_data(con)
    db.close_connection(con)
    return render_template("index.html", tables=tables, columns=columns, total_data=total_data )

''' Create the API to handle docs and all the endpoints for the API.'''
api = Api(
    app,
    title="Best Storage System Ever API",
    version="1.0",
    description="API for the best storage system ever",
    doc="/docs"
)

def create_api_methods():
    @app.get("/")
    def get_items(table):
        ''' Get all items from the table in the database, and return them as a JSON object.'''
        con = db.connect()
        result = db.get_table(con, table)
        db.close_connection(con)
        return result

    @app.get("/primary_key")
    def get_item(table, primary_key):
        ''' Get a single item with the specified ID from the table in the database, and return it as a JSON object.'''
        con = db.connect()
        result = db.get_id(con, table, primary_key)
        db.close_connection(con)
        return result

    @app.post("/")
    def post_item(data):
        ''' Create a new item with the specified ID in the table in the database, and return it as a JSON object.'''
        con = db.connect()
        result = db.insert_data(db.get_insert(con, data))
        db.close_connection(con)
        return result

    @app.delete("/")
    def delete_items(table):
        ''' Delete all items from the table in the database, and return a success message.'''
        con = db.connect()
        result = db.delete_table_data(con, table)
        db.close_connection(con)
        return result
    
    @app.delete("/primary_key")
    def delete_item(table, primary_key, data):
        ''' Delete a single item with the specified ID from the table in the database, and return a success message.'''
        con = db.connect()
        result = db.delete_id(con, table, primary_key, data)
        db.close_connection(con)
        return result

    @app.put("/")
    def update_item(table, column, column_value, primary_key, data):
        ''' Update a single item with the specified ID in the table in the database, and return it as a JSON object.'''
        con = db.connect()
        result = db.update(con, table=table, column=column, val=column_value, primary_key=primary_key, val_id=data)
        db.close_connection(con)
        return result
    
    @app.get("/column")
    def get_column_data(table, column, data):
        ''' Get all data from the column in the table in the database, and return it as a JSON object.'''
        con = db.connect()
        result = db.get_column(con, table, data)
        db.close_connection(con)
        return result

''' Create the API documentation for all the tables and columns in the database.'''
def create_docs():
    con = db.connect()
    tables, columns = db.get_tables_and_columns(db.all_columns(con))
    for table in tables:
        ''' Create a namespace for each table in the database, and create a model for each column in the table.'''
        namespace = api.namespace(table, description=f"Operations related to {table} in the storage system")
        model_fields = {}
        for column in columns[table]:
            ''' Get the data type of the column, and create a model field for it.'''
            data_type = db.get_column_data_type(con, table, column)
            match data_type:
                case "INTEGER":
                    model_fields[column] = fields.Integer(required=True, description=f"{column} of {table}")
                case "REAL":
                    model_fields[column] = fields.Float(required=True, description=f"{column} of {table}")
                case "TEXT":
                    model_fields[column] = fields.String(required=True, description=f"{column} of {table}")
        model = api.model(table, model_fields)

        ''' Create the endpoints for each table in the database, and use the model to validate the input data.'''
        @namespace.route("/")
        class ItemList(Resource):

            @namespace.marshal_list_with(model)
            def get(self, table):
                ''' Get all items from the table in the database, and return them as a JSON object.'''
                return db.get_table(con, table)
        
            @namespace.expect(model)
            @namespace.marshal_with(model, code=201)
            def post(self):
                ''' Create a new item with the specified ID in the table in the database, and return it as a JSON object.'''
                data = api.payload
                return db.insert_data(db.get_insert(con, data)), 201

            @namespace.expect(model)
            @namespace.marshal_list_with(model)
            def delete(self, table):
                ''' Delete all items from the table in the database, and return a success message.'''
                return db.delete_table_data(con, table)



            @namespace.route("/primary_key")
            class ItemList(Resource):
            
                @namespace.marshal_list_with(model)
                def get(self, table, column, primary_key):
                    ''' Get a single item with the specified ID from the table in the database, and return it as a JSON object.'''
                    return db.get_id(con, table, column, primary_key)

                @namespace.expect(model)
                @namespace.marshal_list_with(model, code=202)
                def put(self, table, column, column_val, primary_key, val_id):
                    ''' Update a single item with the specified ID in the table in the database, and return it as a JSON object.'''
                    return db.update(con, table=table, column=column, val=column_val, primary_key=primary_key, val_id=val_id), 202

                @namespace.expect(model)
                @namespace.marshal_list_with(model)
                def delete(self, table, column, primary_key):
                    ''' Delete a single item with the specified ID from the table in the database, and return a success message.'''
                    return db.delete_id(con, table, column, primary_key)
                
            @namespace.route("/column")
            class ItemList(Resource):
                
                @namespace.marshal_list_with(model)
                def get(self, table, column):
                    ''' Get all data from the column in the table in the database, and return it as a JSON object.'''
                    return db.get_column(con, table, column)
    
    db.close_connection(con)

''' Call the function to create the API methods for all the tables and columns in the database.'''
create_api_methods()
''' Call the function to create the API documentation for all the tables and columns in the database.'''
create_docs()

if __name__ == "__main__":
    app.run(debug=True)
    
