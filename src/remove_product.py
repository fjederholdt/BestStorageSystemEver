import sqlite3
import src.DB_commands as db
 
def remove_product(product_id):
    con = db.connect()
    cursor = db.get_cursor(con)
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    db.commit(con)
    db.close_connection(con)


def main(data_base):
    product_id = input("Enter the ID of the product to remove: ")
    remove_product(product_id)


if __name__ == "__main__":
    main(None)