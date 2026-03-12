from faker import Faker
import random
import sqlite3
import DB_commands as db


fake = Faker()


def insert_fake_data(con, n=50):
    cursor = con.cursor()

    names = ["NotSoLet Milk", "Coco Milk", "Banana Milk", "Soy Milk", "Dry Milk"]
    brands = ["Arla", "Crown", "Mammen", "Alpro", "Lurpak"]

    for i in range(n):
        #product_id = 10000 + i
        cursor.execute("SELECT COALESCE(MAX(Product_ID), 9999) FROM Product_Table") # Get the current max Product_ID, start from 10000 if table is empty
        base_id = cursor.fetchone()[0] + 1 # Increment the base_id for the new product
        product_id = base_id + i # Ensure unique Product_ID for each product

        # Product_Table
        cursor.execute("""INSERT INTO Product_Table 
            (Product_ID, Product_Name, Product_Brand, Product_Category, Product_Weight)
            VALUES (?, ?, ?, ?, ?)""", (
            product_id,
            random.choice(names),
            random.choice(brands),
            "Milk",
            str(random.choice([250, 500, 750, 1000])) + "g"
        ))

        # Barcode_Table
        cursor.execute("""INSERT INTO Barcode_Table (Product_ID, Barcode) VALUES (?, ?)""", (
            product_id,
            fake.bothify(text="##########")  # 10-digit barcode
        ))

        # Storage_Table
        cursor.execute("""INSERT INTO Storage_Table (Product_ID, Storage_ID, Stock) VALUES (?, ?, ?)""", (
            product_id,
            random.randint(100, 199),
            random.randint(0, 500)
        ))

        # Price_Table
        cursor.execute("""INSERT INTO Price_Table (Product_ID, Price) VALUES (?, ?)""", (
            product_id,
            round(random.uniform(1000, 10000)) # price in cents to avoid floating point issues
        ))

        # Sales_Table
        cursor.execute("""INSERT INTO Sales_Table (Product_ID, Sale_ID, Quantity, Time_Stamp) VALUES (?, ?, ?, ?)""", (
            product_id,
            100000 + i,
            random.randint(1, 100),
            fake.date_time_between(start_date="-1y", end_date="now").strftime("%d-%m-%Y: %H:%M")
        ))

    con.commit()
if __name__ == "__main__":
    con = sqlite3.connect("LetMilk.db")  
    insert_fake_data(con)
    con.close()
    print("Done!")