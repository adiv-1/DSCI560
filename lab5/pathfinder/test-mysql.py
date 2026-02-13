import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="reddit_user",
    password="your_password",
    database="reddit_db"
)

cursor = conn.cursor()
cursor.execute("SHOW DATABASES;")

for db in cursor:
    print(db)

conn.close()
