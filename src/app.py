import database_commands as db
from flask import Flask, render_template
from flask_restx import Api, Resource, fields

app = Flask(__name__)

@app.route("/")
def home():
    con = db.connect()
    tables, columns = db.get_tables_and_columns(db.all_columns(con))
    total_data = db.get_all_data(con)
    db.close_connection(con)
    return render_template("index.html", tables=tables, columns=columns, total_data=total_data )

api = Api(
    app,
    title="Best Storage System Ever API",
    version="1.0",
    description="API for the best storage system ever",
    doc="/docs"
)

def create_docs():
    con = db.connect()
    tables, columns = db.get_tables_and_columns(db.all_columns(con))
    namespaces = []
    for table in tables:
        namespace = api.namespace(table, description=f"Operations related to {table} in the storage system")
        model_fields = {}
        for column in columns[table]:
            data_type = db.get_column_data_type(con, table, column)
            match data_type:
                case "INTEGER":
                    model_fields[column] = fields.Integer(required=True, description=f"{column} of {table}")
                case "REAL":
                    model_fields[column] = fields.Float(required=True, description=f"{column} of {table}")
                case "TEXT":
                    model_fields[column] = fields.String(required=True, description=f"{column} of {table}")
        model = api.model(table, model_fields)

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


create_docs()

# product_ns = api.namespace("Products", description="Operations related to products in the storage system")

# # Define schema (this becomes the OpenAPI model)
# product_model = api.model("Product", {
#     "Product_ID": fields.Integer(readOnly=True, description="Product ID"),
#     "Product_NAME": fields.String(required=True, description="Product name"),
#     "Product_Brand": fields.String(required=True, description="Product brand"),
#     "Product_Category": fields.String(required=True, description="Product category"),
#     "Product_Weight": fields.Float(required=True, description="Product weight"),
# })

# barcode_ns = api.namespace("Barcodes", description="Operations related to barcodes in the storage system")
# barcode_model = api.model("Barcode", {
#     "Barcode_ID": fields.Integer(readOnly=True, description="Barcode ID"),
#     "Product_ID": fields.Integer(required=True, description="Associated Product ID"),
# })

# storage_ns = api.namespace("Storage", description="Operations related to storage in the storage system")
# storage_model = api.model("Storage", {
#     "Product_ID": fields.Integer(required=True, description="Associated Product ID"),
#     "Storage_ID": fields.Integer(readOnly=True, description="Storage ID"),
#     "Stock": fields.Integer(required=True, description="Stock quantity"),
# })

# price_ns = api.namespace("Prices", description="Operations related to prices in the storage system")
# price_model = api.model("Price", {
#     "Product_ID": fields.Integer(required=True, description="Associated Product ID"),
#     "Price": fields.Float(required=True, description="Product price"),
# })

# sales_ns = api.namespace("Sales", description="Operations related to sales in the storage system")
# sales_model = api.model("Sales", {
#     "Product_ID": fields.Integer(required=True, description="Associated Product ID"),
#     "Sales_ID": fields.Integer(readOnly=True, description="Sales ID"),
#     "Quantity": fields.Integer(required=True, description="Quantity sold"),
#     "Time_Stamp": fields.DateTime(required=True, description="Timestamp of sale"),
# })

    


# @product_ns.route("/")
# class ItemList(Resource):

#     @product_ns.marshal_list_with(product_model)
#     def get(self):
#         """Get all items"""
#         return

#     @product_ns.expect(product_model)
#     @product_ns.marshal_with(product_model, code=201)
#     def post(self):
#         """Create a new item"""
#         item = api.payload
#         return item, 201

# @barcode_ns.route("/")
# class ItemList(Resource):

#     @barcode_ns.marshal_list_with(barcode_model)
#     def get(self):
#         """Get all items"""
#         return get_item()

#     @barcode_ns.expect(barcode_model)
#     @barcode_ns.marshal_with(barcode_model, code=201)
#     def post(self):
#         """Create a new item"""
#         item = api.payload
#         item["id"] = len(items_db) + 1
#         items_db.append(item)
#         return item, 201

# @storage_ns.route("/")
# class ItemList(Resource):

#     @storage_ns.marshal_list_with(storage_model)
#     def get(self):
#         """Get all storage items"""
#         return get_item()

#     @storage_ns.expect(storage_model)
#     @storage_ns.marshal_with(storage_model, code=201)
#     def post(self):
#         """Create a new storage item"""
#         item = api.payload
#         item["id"] = len(items_db) + 1
#         items_db.append(item)
#         return item, 201

# @price_ns.route("/")
# class ItemList(Resource):

#     @price_ns.marshal_list_with(price_model)
#     def get(self):
#         """Get all prices"""
#         return get_item()

#     @price_ns.expect(price_model)
#     @price_ns.marshal_with(price_model, code=201)
#     def post(self):
#         """Create a new price"""
#         item = api.payload
#         item["id"] = len(items_db) + 1
#         items_db.append(item)
#         return item, 201

# @sales_ns.route("/")
# class ItemList(Resource):
    
#     @sales_ns.marshal_list_with(sales_model)
#     def get(self):
#         """Get all sales"""
#         return get_item()

#     @sales_ns.expect(sales_model)
#     @sales_ns.marshal_with(sales_model, code=201)
#     def post(self):
#         """Create a new sale"""
#         item = api.payload
#         item["id"] = len(items_db) + 1
#         items_db.append(item)
#         return item, 201

if __name__ == "__main__":
    app.run(debug=True)
    
