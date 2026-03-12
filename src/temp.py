import DB_commands as db


data = {
        "Product_ID": 12143,
        "Product_NAME": "Soy Milk",
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
'''
con = db.connect()
cursor = db.get_cursor(con)

print(get_insert(data))

db.close_connection(con)'''

con = db.connect()
cursor = con.cursor()
#get_all_data(con)

insert = db.get_insert(data)
#print(insert)
db.insert_data(con,insert)
db.close_connection(con)