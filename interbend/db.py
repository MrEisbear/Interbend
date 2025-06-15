import mysql.connector
from config import Config

db = mysql.connector.connect(
    host=Config.DB_HOST,
    user=Config.DB_USER,
    password=Config.DB_PASSWORD,
    database=Config.DB_NAME
)

def init_db():
    with db.cursor(dictionary=True) as cursor:
        cursor.execute("CREATE TABLE IF NOT EXISTS users ("
                   "bid VARCHAR(32) PRIMARY KEY,"
                   "username VARCHAR(64) NOT NULL,"
                   "email VARCHAR(128) NOT NULL,"
                   "password_hash TEXT,"
                   "balance DECIMAL(18, 2) DEFAULT 7500,"
                   "job INT,"
                   "salary_class INT,"
                   "collected DATETIME"
                   ");")
        cursor.execute("CREATE TABLE IF NOT EXISTS salary ("
                   "class INT PRIMARY KEY,"
                   "money DECIMAL(18, 2));")
        cursor.execute("CREATE TABLE IF NOT EXISTS log("
                       "time DATETIME PRIMARY KEY,"
                       "bid VARCHAR(32),"
                       "action TEXT);")
    db.commit()
    print("Tables Checked!")

def get_user(bid):
    """Fetches a single user from the database by their bid."""
    with db.cursor(dictionary=True) as cur:
        cur.execute("SELECT * FROM users WHERE bid = %s", (bid,))
        return cur.fetchone()