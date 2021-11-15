import sqlite3
from app import config

con = sqlite3.connect(config.ADMIN_DATABASE)
cur = con.cursor()

cur.execute(
    """CREATE TABLE IF NOT EXISTS users 
(pk INTEGER PRIMARY KEY AUTOINCREMENT,
 username TEXT, 
 name TEXT,
 password TEXT,
 activation_date TEXT)"""  # We will store these as ISO8601 strings ("YYYY-MM-DD HH:MM:SS.SSS") in GMT
)
cur.execute("CREATE INDEX IF NOT EXISTS users_username ON users (username)")
cur.execute(
    """CREATE TABLE IF NOT EXISTS email_confirm 
(userid INTEGER,
 nonce TEXT,
 timestamp TEXT)
"""
)
cur.execute("CREATE INDEX IF NOT EXISTS email_confirm_userid on email_confirm (userid)")
