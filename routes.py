from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from models import User

def register_routes(app):

    @app.route('/')
    def home():
        if current_user.is_authenticated:
            if current_user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif current_user.role == 'staff':
                return redirect(url_for('staff_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        return redirect(url_for('login'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('home'))

        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            
            user = User.query.filter_by(email=email).first()
            
            if user and check_password_hash(user.password, password):
                if user.role == 'staff' and user.status != 'approved':
                    flash('Your account is pending admin approval.', 'warning')
                    return redirect(url_for('login'))

                login_user(user)
                
                if user.role == 'admin':
                    return redirect(url_for('admin_dashboard'))
                elif user.role == 'staff':
                    return redirect(url_for('staff_dashboard'))
                else:
                    return redirect(url_for('user_dashboard'))
            else:
                flash('Invalid email or password', 'error')
        
        return render_template('login.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('home'))

        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')
            role = request.form.get('role')
            
            if User.query.filter_by(email=email).first():
                flash('Email already exists', 'error')
                return redirect(url_for('register'))
            
            new_user = User(
                name=name,
                email=email,
                password=generate_password_hash(password),
                role=role,
                status='pending' if role == 'staff' else 'approved'
            )
            
            db.session.add(new_user)
            db.session.commit()
            
            if role == 'staff':
                flash('Registration submitted! Please wait for admin approval.', 'info')
            else:
                flash('Registration successful! Please login.', 'success')
                
            return redirect(url_for('login'))
        
        return render_template('register.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('login'))

    @app.route('/admin/dashboard')
    @login_required
    def admin_dashboard():
        if current_user.role != 'admin':
            flash('Access denied', 'error')
            return redirect(url_for('home'))
        return render_template('admin/dashboard.html')

    @app.route('/staff/dashboard')
    @login_required
    def staff_dashboard():
        if current_user.role != 'staff' or current_user.status != 'approved':
            flash('Access denied or not approved yet', 'error')
            return redirect(url_for('home'))
        return render_template('staff/dashboard.html')

    @app.route('/user/dashboard')
    @login_required
    def user_dashboard():
        if current_user.role != 'trekker':
            flash('Access denied', 'error')
            return redirect(url_for('home'))
        return render_template('user/dashboard.html')
