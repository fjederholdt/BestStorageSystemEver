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
            def get(self):
                """Get all items"""
                return "test"

            @namespace.expect(model)
            @namespace.marshal_with(model, code=201)
            def post(self):
                """Create a new item"""
                item = api.payload
                return item, 201
            
            #TODO: Add put and delete endpoints for each table in the database.
    
    db.close_connection(con)


@app.get("/")
def get_item():
    return {"msg": "Hello World"}

@app.post("/")
def post_item():
    return  "Item created successfully"

@app.put("/")
def update_item():
    return "Item updated successfully"

@app.delete("/")
def delete_item():
    return "Item deleted successfully"

@app.reserve("/")
def reserve_item(primary_key, primary_key_id, quantity, from_location, to_location,status):
    con = db.connect_reserved_db()
    db.reserve_data(con, primary_key, primary_key_id, quantity, from_location, to_location)
    db.update_transit(con,status,primary_key,primary_key_id)
    db.close_connection(con)
    return "Item reserved successfully"

''' Call the function to create the API documentation for all the tables and columns in the database.'''
create_docs()

if __name__ == "__main__":
    app.run(debug=True)
    
