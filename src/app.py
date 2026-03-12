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
def get_item():
    return {"msg": "Hello World"}

@fast_app.post("/")
def insert_item():
    return  "Item created successfully"

@fast_app.put("/")
def update_item(data): #For data structure as list with [table, column, value,column_identifier, value_identifier]
    con = db.connect()
    db.update(con,data[0],data[1],data[2],data[3],data[4]) #for dict: db.update(con,data['table'],data['column'],data['value'],data['column_id'],data['val_id'])
    db.close_connection(con)
    return "Item updated successfully"

@fast_app.delete("/")
def delete_item():
    return "Item deleted successfully"

if __name__ == "__main__":
    app.run(debug=True)

