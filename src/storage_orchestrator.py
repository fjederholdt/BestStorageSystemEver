import sqlite3
from typing import List, Dict, Any
import json

class StorageOrchestrator:
    def __init__(self, db_path: str = "storage.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with products and cart tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL
        )''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS cart (
            id INTEGER PRIMARY KEY,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )''')
        
        conn.commit()
        conn.close()
    
    def add_to_cart(self, product_id: int, quantity: int) -> Dict[str, Any]:
        """Add item to cart"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM cart WHERE product_id = ?", (product_id,))
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute("UPDATE cart SET quantity = quantity + ? WHERE product_id = ?", 
                         (quantity, product_id))
        else:
            cursor.execute("INSERT INTO cart (product_id, quantity) VALUES (?, ?)", 
                         (product_id, quantity))
        
        conn.commit()
        conn.close()
        return {"status": "success", "message": "Added to cart"}
    
    def remove_from_cart(self, product_id: int) -> Dict[str, Any]:
        """Remove item from cart"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cart WHERE product_id = ?", (product_id,))
        conn.commit()
        conn.close()
        return {"status": "success", "message": "Removed from cart"}
    
    def get_cart(self) -> List[Dict[str, Any]]:
        """Get all cart items"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''SELECT p.id, p.name, p.price, c.quantity, (p.price * c.quantity) as total
                         FROM cart c JOIN products p ON c.product_id = p.id''')
        rows = cursor.fetchall()
        conn.close()
        
        return [{"id": r[0], "name": r[1], "price": r[2], "quantity": r[3], "total": r[4]} 
                for r in rows]
    
    def checkout(self) -> Dict[str, Any]:
        """Process checkout and clear cart"""
        cart = self.get_cart()
        total = sum(item["total"] for item in cart)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cart")
        conn.commit()
        conn.close()
        
        return {"status": "success", "total": total, "items": cart}