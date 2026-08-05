from extensions import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # will store hashed password
    role = db.Column(db.String(20), nullable=False)  # 'admin', 'staff', 'trekker'
    status = db.Column(db.String(20), default='approved')  # 'pending','approved','blacklisted'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
class Trek(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trek_name = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)  # Easy/Moderate/Hard
    duration = db.Column(db.Integer, nullable=False)  # in days
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    available_slots = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='Open')  # Open/Closed/Completed

    assigned_staff_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    assigned_staff = db.relationship('User', backref='assigned_treks')
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey('trek.id'), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    booking_status = db.Column(db.String(20), default='Booked')  # Booked/Cancelled/Completed
    payment_status = db.Column(db.String(20), default='Pending')

    user = db.relationship('User', backref='bookings')
    trek = db.relationship('Trek', backref='bookings')
