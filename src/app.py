from fastapi import FastAPI, HTTPException
import database_commands as db
from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    con = db.connect()
    tables, columns = db.get_tables_and_columns(db.all_columns(con))
    total_data = db.get_all_data(con)
    db.close_connection(con)
    return render_template("index.html", tables=tables, columns=columns, total_data=total_data )

fast_app = FastAPI()

@fast_app.get("/")
def get_item(table=None,column=None,id=None):
    print(table,column,id)
    con = db.connect()

    if id is not None:
        data = db.get_id(con, table, column,id)
    elif column is not None:
        data = db.get_column(con, table, column)
    elif table is not None:
        data = db.get_table(con, table)

    db.close_connection(con)
    return data

@fast_app.post("/")
def insert_item():
    return  "Item created successfully"

@fast_app.put("/")
def update_item():
    return "Item updated successfully"

@fast_app.delete("/")
def delete_item():
    return "Item deleted successfully"

if __name__ == "__main__":
    app.run(debug=True)
