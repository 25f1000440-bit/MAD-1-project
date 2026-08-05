import os
from flask import Flask
from extensions import db
from config import Config
from models import User, Trek, Booking

app = Flask(__name__, instance_relative_config=True)
app.config.from_object(Config)
os.makedirs(app.instance_path, exist_ok=True)
db.init_app(app)
with app.app_context():
    db.create_all()
if __name__ == '__main__':
    with app.app_context():
        db.create_all()          
    app.run(debug=True)
