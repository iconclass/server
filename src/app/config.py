import os


DEBUG = os.environ.get("DEBUG", "0") == "1"
# to get a string like this run:
# openssl rand -hex 32
# eg. 1eb17803589deacdebca88c996e192da7c55594f64ca20e324c9ab0be4cf6049
SECRET_KEY = os.environ.get("SECRET_KEY", "foobarbaz")
VERSION = os.environ.get("VERSION", "0.1")
ADMIN_DATABASE = os.environ.get("ADMIN_DATABASE", "admin.sqlite")
ORIGINS = os.environ.get(
    "ORIGINS",
    "http://localhost:8080",
).split(" ")
ACCESS_TOKEN_EXPIRE_DAYS = int(os.environ.get("ACCESS_TOKEN_EXPIRE_DAYS", "30"))
