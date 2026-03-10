import sqlite3
import DB_commands as db
# filename to form database
file = "LetMilk.db"

try:
  con = sqlite3.connect(file)
  print(f"Database {file}.db formed.")

  db.create_table(con, f"""CREATE TABLE IF NOT EXISTS Product_Table (
        Product_ID INTEGER PRIMARY KEY,
        Product_NAME TEXT NOT NULL,
        Product_Brand TEXT NOT NULL,
        Product_Category TEXT NOT NULL,
        Product_Weight REAL NOT NULL
                                    );""")
  db.create_table(con,"""CREATE TABLE IF NOT EXISTS Barcode_Table (
        Barcode INTEGER NOT NULL,
        Product_ID INTEGER PRIMARY KEY
                                    );""")
  db.create_table(con, f"""CREATE TABLE IF NOT EXISTS Storage_Table (
        Product_ID INTEGER PRIMARY KEY,
        Storage_ID INTEGER NOT NULL,
        Stock INTEGER NOT NULL
                                    );""")
  db.create_table(con, f"""CREATE TABLE IF NOT EXISTS Price_Table (
        Product_ID INTEGER PRIMARY KEY,
        Price REAL NOT NULL,
        Campagin_Date TEXT NOT NULL
                                    );""")
  db.create_table(con, f"""CREATE TABLE IF NOT EXISTS Sales_Table (
        Product_ID INTEGER PRIMARY KEY,
        Sale_ID INTEGER NOT NULL,
        Quantity INTEGER NOT NULL,
        
                                    );""")

except:
  print("Database not formed.")