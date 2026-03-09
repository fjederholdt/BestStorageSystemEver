import sqlite3
import src.DB_commands as db

def main(args=None):
    con = db.connect()
    cursor = db.get_cursor(con)

    db.create_table(con, f"""CREATE TABLE IF NOT EXISTS {args['product']} (
        {args['Desc']} TEXT NOT NULL,
        {args['ID']} INTEGER PRIMARY KEY,
        {args['Expire Date']} TEXT NOT NULL,
        {args['Weight']} REAL NOT NULL,
        {args['Batch']} TEXT NOT NULL,
        {args['Manufacturer']} TEXT NOT NULL,
        {args['Cost_Price']} REAL NOT NULL,
        {args['Retail_Price']} REAL NOT NULL,
        {args['VAT']} REAL NOT NULL
    );""")
    



if __name__ == "__main__":
    main()