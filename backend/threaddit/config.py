from dotenv import dotenv_values

POSTGRES_USER = dotenv_values(".env")["POSTGRES_USER"]
POSTGRES_PASSWORD = dotenv_values(".env")["POSTGRES_PASSWORD"]
SECRET_KEY = dotenv_values(".env")["SECRET_KEY"]
