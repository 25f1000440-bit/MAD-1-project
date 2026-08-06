from flask import Flask
from flask_login import LoginManager
from extensions import db
from config import Config
from models import User, Trek, Booking
from routes import register_routes

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# Set up Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register all routes onto the app instance
register_routes(app)

# Create database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
