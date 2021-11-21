import sqlite3
from app import config

con = sqlite3.connect(config.ADMIN_DATABASE)
cur = con.cursor()

cur.execute(
    """CREATE TABLE IF NOT EXISTS users 
(username TEXT, 
 name TEXT,
 password TEXT,
 activation_date TEXT)"""  # We will store these as ISO8601 strings ("YYYY-MM-DD HH:MM:SS.SSS") in GMT
)
cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS users_username ON users (username)")
cur.execute("CREATE TABLE IF NOT EXISTS email_confirm (username TEXT, nonce TEXT)")
cur.execute(
    "CREATE INDEX IF NOT EXISTS email_confirm_username on email_confirm (username)"
)
cur.execute("CREATE INDEX IF NOT EXISTS email_confirm_nonce on email_confirm (nonce)")
# The nonce used in the email_confim is a ksuid https://segment.com/blog/a-brief-history-of-the-uuid/
# so it has a timestamp baked in
