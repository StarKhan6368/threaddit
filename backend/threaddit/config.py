from dotenv import dotenv_values

DATABASE_URI = dotenv_values(".env")["DATABASE_URI"]
SECRET_KEY = dotenv_values(".env")["SECRET_KEY"]
