import os

# class Config(object):
#     SECRET_KEY = os.urandom(32)
#     basedir = os.path.abspath(os.path.dirname(__file__))  # the script folder
#     SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disable track modifications warning
#     DEBUG = True  # automatically restarts the app upon modifications
#     DATABASE_NAME = "fyyur"
#     username = "postgres"
#     password = "postgres"
#     url = "localhost:5432"

#     def DATABASE_URI(self):
#         # Connect to the database
#         SQLALCHEMY_DATABASE_URI = \
#             f"postgres://{self.username}:{self.password}@{self.url}/{self.DATABASE_NAME}"
#         # SQLALCHEMY_DATABASE_URI = "postgres://postgres:postgres@localhost:5432/fyyur"
#         return SQLALCHEMY_DATABASE_URI

SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database

# DONE implement database url
SQLALCHEMY_DATABASE_URI = "postgres://postgres:postgres@localhost:5432/fyyur"
SQLALCHEMY_TRACK_MODIFICATIONS = False
