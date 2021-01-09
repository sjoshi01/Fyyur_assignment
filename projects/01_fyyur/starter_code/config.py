import os
from flask import Flask

app = Flask(__name__)
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# TODO IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = 'postgres://sayali@localhost:5432/fyyurappdb'
SQLALCHEMY_TRACK_MODIFICATIONS = False   ## Added to make sure no double quotes were added to table names

# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI']=SQLALCHEMY_DATABASE_URI

