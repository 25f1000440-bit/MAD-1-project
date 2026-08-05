import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Points to /Project/instance/database.db
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'instance', 'database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
