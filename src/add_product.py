import sqlite3
import src.DB_commands as db

def main(args=None):
    con = db.connect()
    cur = db.get_cursor(con)

    db.create_table(con, f"""CREATE TABLE IF NOT EXISTS {args['product']} (
        {args['Desc']} TEXT NOT NULL,
        {args['id']} INTEGER PRIMARY KEY,
        {args['Expire Date']} TEXT NOT NULL,
        quantity INTEGER NOT NULL
    );""")
    



if __name__ == "__main__":
    main()