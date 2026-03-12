from fastapi import FastAPI, HTTPException
import database_commands as db
from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    con = db.connect()
    cursor = db.get_cursor(con)
    schema = db.all_columns(con)
    tables = []
    columns = {}
    column_sizes = {}
    total_data = [],[],[]
    for table, column in schema.items():
        tables.append(table)
        columns[table] = column
        column_sizes[table] = len(column)
        for item in column:
            cursor.execute(f"SELECT {item} FROM {table}")
            data = cursor.fetchall()
            total_data[item] = data

    db.close_connection(con)
    return render_template("index.html", tables=tables, columns=columns, column_sizes=column_sizes, total_data=total_data )

fast_app = FastAPI()

@fast_app.get("/")
def get_item():
    return {"msg": "Hello World"}

@fast_app.post("/")
def insert_item():
    return  "Item created successfully"

fast_app.put()
def update_item():
    return "Item updated successfully"

@fast_app.delete("/")
def delete_item():
    return "Item deleted successfully"

if __name__ == "__main__":
    app.run(debug=True)
