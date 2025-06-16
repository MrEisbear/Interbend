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
                   "collected DATETIME"
                   ");")
        cursor.execute("CREATE TABLE IF NOT EXISTS salary ("
                   "class INT PRIMARY KEY,"
                   "money DECIMAL(18, 2));")
        cursor.execute("CREATE TABLE IF NOT EXISTS log("
                       "time DATETIME PRIMARY KEY,"
                       "bid VARCHAR(32),"
                       "action TEXT);")
        cursor.execute("CREATE TABLE IF NOT EXISTS jobs("
                       "job_id INT PRIMARY KEY AUTO_INCREMENT,"
                       "job_name VARCHAR(100) NOT NULL,"
                       "salary_class INT NOT NULL"
                       ");")
        cursor.execute("CREATE TABLE IF NOT EXISTS user_jobs("
                       "user_bid VARCHAR(32) NOT NULL,"
                       "job_id INT NOT NULL,"
                       "collected DATETIME,"
                       "PRIMARY KEY (user_bid, job_id),"
                       "FOREIGN KEY (user_bid) REFERENCES users(bid),"
                       "FOREIGN KEY (job_id) REFERENCES jobs(job_id)"
                       ")")
    db.commit()
    print("Tables Checked!")

def get_user(bid):
    """Fetches a single user from the database by their bid."""
    with db.cursor(dictionary=True) as cur:
        cur.execute("SELECT * FROM users WHERE bid = %s", (bid,))
        return cur.fetchone()