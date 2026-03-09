from faker import Faker
import random

fake = Faker()

def insert_fake_data(con, table_name, n=50):
    cursor = con.cursor()

    for i in range(n):
        desc = fake.word()
        expire = fake.date_between(start_date="+30d", end_date="+2y")
        weight = round(random.uniform(0.1, 5.0), 2)
        batch = fake.bothify(text="??##")
        manufacturer = fake.company()

        cost = round(random.uniform(5, 50), 2)
        retail = round(cost * random.uniform(1.3, 1.8), 2)
        vat = 0.25
        
        cursor.execute(f"""
        INSERT INTO {table_name}
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            desc,
            i+1,
            expire,
            weight,
            batch,
            manufacturer,
            cost,
            retail,
            vat
        ))

    con.commit()