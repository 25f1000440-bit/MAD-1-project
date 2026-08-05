'''from app import app
from extensions import db
from models import User, Trek, Booking
from werkzeug.security import generate_password_hash
from datetime import date

with app.app_context():
    # Step A: Create a dummy Trek Staff user
    staff = User(
        name='Vikas Singh',
        email='vikas@mail.com',
        password=generate_password_hash('staff123'),
        role='staff',
        status='approved'
    )
    db.session.add(staff)
    db.session.commit()  # commit now so staff.id gets generated

    # Step B: Create a dummy Trekker (normal user)
    trekker = User(
        name='Amit Sharma',
        email='amit@mail.com',
        password=generate_password_hash('user123'),
        role='trekker',
        status='approved'
    )
    db.session.add(trekker)
    db.session.commit()

    # Step C: Create a dummy Trek, assigned to that staff member
    trek = Trek(
        trek_name='Everest Base Camp',
        location='Nepal',
        difficulty='Hard',
        duration=12,
        start_date=date(2026, 5, 20),
        end_date=date(2026, 5, 31),
        available_slots=10,
        status='Open',
        assigned_staff_id=staff.id
    )
    db.session.add(trek)
    db.session.commit()

    # Step D: Create a dummy Booking linking trekker + trek
    booking = Booking(
        user_id=trekker.id,
        trek_id=trek.id,
        booking_status='Booked',
        payment_status='Paid'
    )
    db.session.add(booking)
    db.session.commit()

    print("Test data created successfully!")'''
from app import app
from models import Trek, Booking

with app.app_context():
    trek = Trek.query.first()
    print("Trek:", trek.trek_name)
    print("Assigned Staff:", trek.assigned_staff.name)   # tests Trek ↔ User relationship

    booking = Booking.query.first()
    print("Booking User:", booking.user.name)     # tests Booking ↔ User
    print("Booking Trek:", booking.trek.trek_name) # tests Booking ↔ Trek
