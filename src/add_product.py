import DB_commands as db

def add_product(data):
    con = db.connect()
    print("Inserting Product")
    db.insert_table(con, """INSERT INTO Product_Table (
                    Product_ID, 
                    Product_Name, 
                    Product_Brand, 
                    Product_Category, 
                    Product_Weight 
                        ) VALUES (?, ?, ?, ?, ?);""", (
        data['Product_ID'],
        data['Product_Name'],
        data['Product_Brand'],
        data['Product_Category'],
        data['Product_Weight']
    ))
    print("Inserting Barcode")
    db.insert_table(con, """INSERT INTO Barcode_Table (
                    Product_ID, 
                    Barcode 
                        ) VALUES (?, ?);""", (
        data['Product_ID'],
        data['Barcode']
    ))
    print("Inserting Storage")
    db.insert_table(con, """INSERT INTO Storage_Table (
                    Product_ID, 
                    Storage_ID,
                    Stock
                        ) VALUES (?, ?, ?);""", (
        data['Product_ID'],
        data['Storage_ID'],
        data['Stock']
    ))
    print("Inserting Price")
    db.insert_table(con, """INSERT INTO Price_Table (
                    Product_ID, 
                    Price
                        ) VALUES (?, ?);""", (
        data['Product_ID'],
        data['Price']
    ))
    print("Inserting Sales")
    db.insert_table(con, """INSERT INTO Sales_Table (
                    Product_ID, 
                    Sale_ID,
                    Quantity,
                    Time_Stamp
                        ) VALUES (?, ?, ?, ?);""", (
        data['Product_ID'],
        data['Sale_ID'],
        data['Quantity'],
        data['Time_Stamp']
    ))
    #cursor = db.get_cursor(con)
    db.commit(con)
    db.close_connection(con)

if __name__ == "__main__":
    data = {
        "Product_ID": 12131,
        "Product_Name": "Soy Milk",
        "Product_Brand": "Arla",
        "Product_Category": "Food",
        "Product_Weight": "500g",
        "Barcode": 1111111111,
        "Storage_ID": 111,
        "Stock": 10,
        "Price": 15,
        "Sale_ID": 111111,
        "Quantity": 3,
        "Time_Stamp": "09-03-2026: 14:00"
    }
    #data = int(sys.argv[1]")

    add_product(data)