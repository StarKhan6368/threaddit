from dotenv import dotenv_values

DATABASE_URI = dotenv_values()["DATABASE_URI"]
SECRET_KEY = dotenv_values()["SECRET_KEY"]
CLOUDINARY_NAME = dotenv_values()["CLOUDINARY_NAME"]
CLOUDINARY_API_KEY = dotenv_values()["CLOUDINARY_API_KEY"]
CLOUDINARY_API_SECRET = dotenv_values()["CLOUDINARY_API_SECRET"]
JWT_ACCESS_EXPIRE_MINUTES = int(dotenv_values()["JWT_ACCESS_EXPIRE_MINUTES"])
JWT_REFRESH_EXPIRE_MINUTES = int(dotenv_values()["JWT_REFRESH_EXPIRE_MINUTES"])
