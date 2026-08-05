from app import app
from extensions import db
from models import User
from werkzeug.security import generate_password_hash

def create_admin():
    with app.app_context():
        # Step A: Check if an admin already exists (avoid duplicates)
        existing_admin = User.query.filter_by(role='admin').first()
        
        if existing_admin:
            print("Admin already exists:", existing_admin.email)
            return
        
        # Step B: Create the admin user
        admin = User(
            name='Admin',
            email='admin@trekapp.com',
            password=generate_password_hash('admin123'),  # hashed, not plain text
            role='admin',
            status='approved'
        )
        
        # Step C: Save to database
        db.session.add(admin)
        db.session.commit()
        print("Admin created successfully!")
        print("Email: admin@trekapp.com")
        print("Password: admin123")

if __name__ == '__main__':
    create_admin()
