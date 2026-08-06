from datetime import datetime
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from models import User, Trek, Booking

def register_routes(app):

    # ============ HOME ============
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

    # ============ LOGIN ============
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

    # ============ REGISTER ============
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

    # ============ LOGOUT ============
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('login'))

    # ============ ADMIN DASHBOARD ============
    @app.route('/admin/dashboard')
    @login_required
    def admin_dashboard():
        if current_user.role != 'admin':
            flash('Access denied', 'error')
            return redirect(url_for('home'))
        
        total_treks = Trek.query.count()
        total_users = User.query.filter_by(role='trekker').count()
        total_staff = User.query.filter_by(role='staff').count()
        total_bookings = Booking.query.count()
        
        recent_bookings = Booking.query.order_by(Booking.booking_date.desc()).limit(5).all()
        
        return render_template('admin/dashboard.html',
                               total_treks=total_treks,
                               total_users=total_users,
                               total_staff=total_staff,
                               total_bookings=total_bookings,
                               recent_bookings=recent_bookings)

    # ============ ADMIN - MANAGE TREKS ============
    @app.route('/admin/manage-treks')
    @login_required
    def manage_treks():
        if current_user.role != 'admin':
            flash('Access denied', 'error')
            return redirect(url_for('home'))
        
        treks = Trek.query.all()
        return render_template('admin/manage_treks.html', treks=treks)

    # ============ ADMIN - ADD TREK ============
    @app.route('/admin/add-trek', methods=['GET', 'POST'])
    @login_required
    def add_trek():
        if current_user.role != 'admin':
            flash('Access denied', 'error')
            return redirect(url_for('home'))
        
        if request.method == 'POST':
            trek_name = request.form.get('trek_name')
            location = request.form.get('location')
            difficulty = request.form.get('difficulty')
            duration = request.form.get('duration')
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            available_slots = request.form.get('available_slots')
            assigned_staff_id = request.form.get('assigned_staff_id')
            
            try:
                duration = int(duration)
                available_slots = int(available_slots)
                assigned_staff_id = int(assigned_staff_id) if assigned_staff_id else None
            except ValueError:
                flash('Invalid input data', 'error')
                return redirect(url_for('add_trek'))
            
            new_trek = Trek(
                trek_name=trek_name,
                location=location,
                difficulty=difficulty,
                duration=duration,
                start_date=datetime.strptime(start_date, '%Y-%m-%d').date(),
                end_date=datetime.strptime(end_date, '%Y-%m-%d').date(),
                available_slots=available_slots,
                assigned_staff_id=assigned_staff_id,
                status='Open'
            )
            
            db.session.add(new_trek)
            db.session.commit()
            
            flash('Trek added successfully!', 'success')
            return redirect(url_for('manage_treks'))
        
        staff_members = User.query.filter_by(role='staff', status='approved').all()
        return render_template('admin/add_edit_trek.html', staff_members=staff_members, trek=None)

    # ============ ADMIN - EDIT TREK ============
    @app.route('/admin/edit-trek/<int:trek_id>', methods=['GET', 'POST'])
    @login_required
    def edit_trek(trek_id):
        if current_user.role != 'admin':
            flash('Access denied', 'error')
            return redirect(url_for('home'))
        
        trek = Trek.query.get_or_404(trek_id)
        
        if request.method == 'POST':
            trek.trek_name = request.form.get('trek_name')
            trek.location = request.form.get('location')
            trek.difficulty = request.form.get('difficulty')
            trek.duration = int(request.form.get('duration'))
            trek.start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
            trek.end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date()
            trek.available_slots = int(request.form.get('available_slots'))
            assigned_staff_id = request.form.get('assigned_staff_id')
            trek.assigned_staff_id = int(assigned_staff_id) if assigned_staff_id else None
            
            db.session.commit()
            
            flash('Trek updated successfully!', 'success')
            return redirect(url_for('manage_treks'))
        
        staff_members = User.query.filter_by(role='staff', status='approved').all()
        return render_template('admin/add_edit_trek.html', trek=trek, staff_members=staff_members)

    # ============ ADMIN - DELETE TREK ============
    @app.route('/admin/delete-trek/<int:trek_id>', methods=['POST'])
    @login_required
    def delete_trek(trek_id):
        if current_user.role != 'admin':
            flash('Access denied', 'error')
            return redirect(url_for('home'))
        
        trek = Trek.query.get_or_404(trek_id)
        Booking.query.filter_by(trek_id=trek_id).delete()
        
        db.session.delete(trek)
        db.session.commit()
        
        flash('Trek deleted successfully!', 'success')
        return redirect(url_for('manage_treks'))

    # ============ ADMIN - MANAGE STAFF ============
    @app.route('/admin/manage-staff')
    @login_required
    def manage_staff():
        if current_user.role != 'admin':
            flash('Access denied', 'error')
            return redirect(url_for('home'))
        
        pending_staff = User.query.filter_by(role='staff', status='pending').all()
        approved_staff = User.query.filter_by(role='staff', status='approved').all()
        blacklisted_staff = User.query.filter_by(role='staff', status='blacklisted').all()
        
        return render_template('admin/manage_staff.html',
                               pending_staff=pending_staff,
                               approved_staff=approved_staff,
                               blacklisted_staff=blacklisted_staff)

    # ============ ADMIN - APPROVE STAFF ============
    @app.route('/admin/approve-staff/<int:staff_id>', methods=['POST'])
    @login_required
    def approve_staff(staff_id):
        if current_user.role != 'admin':
            flash('Access denied', 'error')
            return redirect(url_for('home'))
        
        staff = User.query.get_or_404(staff_id)
        
        if staff.role == 'staff':
            staff.status = 'approved'
            db.session.commit()
            flash(f'{staff.name} approved successfully!', 'success')
        
        return redirect(url_for('manage_staff'))

    # ============ ADMIN - BLACKLIST STAFF ============
    @app.route('/admin/blacklist-staff/<int:staff_id>', methods=['POST'])
    @login_required
    def blacklist_staff(staff_id):
        if current_user.role != 'admin':
            flash('Access denied', 'error')
            return redirect(url_for('home'))
        
        staff = User.query.get_or_404(staff_id)
        
        if staff.role == 'staff':
            staff.status = 'blacklisted'
            db.session.commit()
            flash(f'{staff.name} blacklisted successfully!', 'success')
        
        return redirect(url_for('manage_staff'))

    # ============ STAFF DASHBOARD ============
    @app.route('/staff/dashboard')
    @login_required
    def staff_dashboard():
        if current_user.role != 'staff' or current_user.status != 'approved':
            flash('Access denied or not approved yet', 'error')
            return redirect(url_for('home'))
        
        assigned_treks = Trek.query.filter_by(assigned_staff_id=current_user.id).all()
        
        total_assigned_treks = len(assigned_treks)
        open_treks = len([t for t in assigned_treks if t.status == 'Open'])
        
        total_participants = 0
        for trek in assigned_treks:
            total_participants += Booking.query.filter_by(trek_id=trek.id, booking_status='Booked').count()
        
        return render_template('staff/dashboard.html',
                               assigned_treks=assigned_treks,
                               total_assigned_treks=total_assigned_treks,
                               open_treks=open_treks,
                               total_participants=total_participants)

    # ============ STAFF - MANAGE TREK ============
    @app.route('/staff/manage-trek/<int:trek_id>', methods=['GET', 'POST'])
    @login_required
    def manage_trek(trek_id):
        if current_user.role != 'staff' or current_user.status != 'approved':
            flash('Access denied', 'error')
            return redirect(url_for('home'))
        
        trek = Trek.query.get_or_404(trek_id)
        
        if trek.assigned_staff_id != current_user.id:
            flash('You are not assigned to this trek', 'error')
            return redirect(url_for('staff_dashboard'))
        
        if request.method == 'POST':
            action = request.form.get('action')
            
            if action == 'update_slots':
                new_slots = request.form.get('available_slots')
                try:
                    trek.available_slots = int(new_slots)
                    db.session.commit()
                    flash('Slots updated successfully!', 'success')
                except ValueError:
                    flash('Invalid slot number', 'error')
            
            elif action == 'update_status':
                new_status = request.form.get('status')
                trek.status = new_status
                db.session.commit()
                flash(f'Trek status updated to {new_status}!', 'success')
            
            return redirect(url_for('manage_trek', trek_id=trek.id))
        
        bookings = Booking.query.filter_by(trek_id=trek.id).all()
        return render_template('staff/manage_trek.html', trek=trek, bookings=bookings)

    # ============ USER DASHBOARD ============
    @app.route('/user/dashboard')
    @login_required
    def user_dashboard():
        if current_user.role != 'trekker':
            flash('Access denied', 'error')
            return redirect(url_for('home'))
        return render_template('user/dashboard.html')
