import os

SECRET_KEY = os.urandom(32)
basedir = os.path.abspath(os.path.dirname(__file__))  # the script folder
SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disable track modifications warning
DEBUG = True  # automatically restarts the app upon modifications


class DatabaseURI:
    # Connect to the database
    DATABASE_NAME = "fyyur"
    username = "postgres"
    password = "postgres"
    url = "localhost:5432"
    SQLALCHEMY_DATABASE_URI = f"postgres://{username}:{password}@{url}/{DATABASE_NAME}"
    # SQLALCHEMY_DATABASE_URI = "postgres://postgres:postgres@localhost:5432/fyyur"

# DONE implement database url
