import sqlite3

# filename to form database
file = "LetMilk.db"

try:
  conn = sqlite3.connect(file)
  print("Database LetMilk.db formed.")
except:
  print("Database LetMilk.db not formed.")