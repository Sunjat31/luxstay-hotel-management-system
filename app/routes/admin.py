from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models import Room, RoomType, Booking, User, Staff, Service
from app.forms import RoomForm, RoomTypeForm, StaffForm, ServiceForm
import os
from werkzeug.utils import secure_filename

admin = Blueprint('admin', __name__)


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Admin access required.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated


@admin.route('/dashboard')
@login_required
@admin_required
def dashboard():
    stats = {
        'total_rooms': Room.query.count(),
        'available': Room.query.filter_by(status='available').count(),
        'occupied': Room.query.filter_by(status='occupied').count(),
        'maintenance': Room.query.filter_by(status='maintenance').count(),
        'total_users': User.query.filter_by(role='guest').count(),
        'total_bookings': Booking.query.count(),
        'active_bookings': Booking.query.filter(Booking.status.in_(['confirmed', 'checked_in'])).count(),
        'total_staff': Staff.query.count(),
    }
    recent_bookings = Booking.query.order_by(Booking.created_at.desc()).limit(10).all()
    return render_template('admin_dash.html', stats=stats, recent_bookings=recent_bookings)


# ---------- ROOMS ----------
@admin.route('/rooms')
@login_required
@admin_required
def manage_rooms():
    rooms = Room.query.order_by(Room.floor, Room.room_number).all()
    return render_template('admin/rooms.html', rooms=rooms)


@admin.route('/rooms/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_room():
    form = RoomForm()
    form.room_type_id.choices = [(rt.id, rt.name) for rt in RoomType.query.all()]
    if form.validate_on_submit():
        room = Room(
            room_number=form.room_number.data,
            floor=form.floor.data,
            room_type_id=form.room_type_id.data,
            status=form.status.data,
            capacity=form.capacity.data,
            amenities=form.amenities.data
        )
        db.session.add(room)
        db.session.commit()
        flash(f'Room {room.room_number} added successfully.', 'success')
        return redirect(url_for('admin.manage_rooms'))
    return render_template('admin/room_form.html', form=form, title='Add Room')


@admin.route('/rooms/edit/<int:room_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_room(room_id):
    room = Room.query.get_or_404(room_id)
    form = RoomForm(obj=room)
    form.room_type_id.choices = [(rt.id, rt.name) for rt in RoomType.query.all()]
    if form.validate_on_submit():
        room.room_number = form.room_number.data
        room.floor = form.floor.data
        room.room_type_id = form.room_type_id.data
        room.status = form.status.data
        room.capacity = form.capacity.data
        room.amenities = form.amenities.data
        db.session.commit()
        flash(f'Room {room.room_number} updated.', 'success')
        return redirect(url_for('admin.manage_rooms'))
    return render_template('admin/room_form.html', form=form, title='Edit Room', room=room)


@admin.route('/rooms/delete/<int:room_id>', methods=['POST'])
@login_required
@admin_required
def delete_room(room_id):
    room = Room.query.get_or_404(room_id)
    if room.bookings:
        flash('Cannot delete room with existing bookings.', 'danger')
    else:
        db.session.delete(room)
        db.session.commit()
        flash('Room deleted.', 'success')
    return redirect(url_for('admin.manage_rooms'))


# ---------- ROOM TYPES ----------
@admin.route('/room-types')
@login_required
@admin_required
def manage_room_types():
    types = RoomType.query.all()
    return render_template('admin/room_types.html', types=types)


@admin.route('/room-types/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_room_type():
    form = RoomTypeForm()
    if form.validate_on_submit():
        rt = RoomType(name=form.name.data, description=form.description.data,
                      base_price=form.base_price.data)
        db.session.add(rt)
        db.session.commit()
        flash('Room type added.', 'success')
        return redirect(url_for('admin.manage_room_types'))
    return render_template('admin/room_type_form.html', form=form, title='Add Room Type')


# ---------- BOOKINGS ----------
@admin.route('/bookings')
@login_required
@admin_required
def manage_bookings():
    status = request.args.get('status', '')
    query = Booking.query
    if status:
        query = query.filter_by(status=status)
    bookings = query.order_by(Booking.created_at.desc()).all()
    return render_template('admin/bookings.html', bookings=bookings, selected_status=status)


@admin.route('/bookings/update-status/<int:booking_id>', methods=['POST'])
@login_required
@admin_required
def update_booking_status(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    new_status = request.form.get('status')
    valid = ['confirmed', 'checked_in', 'checked_out', 'cancelled']
    if new_status in valid:
        booking.status = new_status
        if new_status == 'checked_in':
            booking.room.status = 'occupied'
        elif new_status in ('checked_out', 'cancelled'):
            booking.room.status = 'available'
        db.session.commit()
        flash(f'Booking #{booking.id} status updated to {new_status}.', 'success')
    return redirect(url_for('admin.manage_bookings'))


# ---------- USERS ----------
@admin.route('/users')
@login_required
@admin_required
def manage_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)


# ---------- STAFF ----------
@admin.route('/staff')
@login_required
@admin_required
def manage_staff():
    staff = Staff.query.order_by(Staff.full_name).all()
    return render_template('admin/staff.html', staff=staff)


@admin.route('/staff/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_staff():
    form = StaffForm()
    if form.validate_on_submit():
        member = Staff(
            full_name=form.full_name.data,
            position=form.position.data,
            department=form.department.data,
            phone=form.phone.data,
            email=form.email.data,
            salary=form.salary.data
        )
        db.session.add(member)
        db.session.commit()
        flash('Staff member added.', 'success')
        return redirect(url_for('admin.manage_staff'))
    return render_template('admin/staff_form.html', form=form, title='Add Staff')


@admin.route('/staff/delete/<int:staff_id>', methods=['POST'])
@login_required
@admin_required
def delete_staff(staff_id):
    member = Staff.query.get_or_404(staff_id)
    db.session.delete(member)
    db.session.commit()
    flash('Staff member removed.', 'success')
    return redirect(url_for('admin.manage_staff'))


# ---------- SERVICES ----------
def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@admin.route('/services')
@login_required
@admin_required
def manage_services():
    services = Service.query.all()
    return render_template('admin/services.html', services=services)


@admin.route('/services/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_service():
    form = ServiceForm()
    if form.validate_on_submit():
        # Handle file upload
        image_filename = None
        if form.image.data:
            file = form.image.data
            if file and allowed_file(file.filename):
                from flask import current_app
                filename = secure_filename(f"{form.name.data.replace(' ', '_')}_{os.urandom(8).hex()}.{file.filename.rsplit('.', 1)[1].lower()}")
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                image_filename = filename
        
        service = Service(
            name=form.name.data,
            description=form.description.data,
            image_path=image_filename,
            category=form.category.data,
            features=form.features.data,
            icon_class=form.icon_class.data
        )
        db.session.add(service)
        db.session.commit()
        flash(f'Service "{service.name}" added successfully.', 'success')
        return redirect(url_for('admin.manage_services'))
    return render_template('admin/service_form.html', form=form, title='Add Service')


@admin.route('/services/edit/<int:service_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_service(service_id):
    service = Service.query.get_or_404(service_id)
    form = ServiceForm()
    if form.validate_on_submit():
        # Handle file upload
        if form.image.data:
            file = form.image.data
            if file and allowed_file(file.filename):
                # Delete old image if exists
                if service.image_path:
                    from flask import current_app
                    old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], service.image_path)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                
                from flask import current_app
                filename = secure_filename(f"{form.name.data.replace(' ', '_')}_{os.urandom(8).hex()}.{file.filename.rsplit('.', 1)[1].lower()}")
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                service.image_path = filename
        
        service.name = form.name.data
        service.description = form.description.data
        service.category = form.category.data
        service.features = form.features.data
        service.icon_class = form.icon_class.data
        db.session.commit()
        flash(f'Service "{service.name}" updated.', 'success')
        return redirect(url_for('admin.manage_services'))
    elif request.method == 'GET':
        form.name.data = service.name
        form.description.data = service.description
        form.category.data = service.category
        form.features.data = service.features
        form.icon_class.data = service.icon_class
    return render_template('admin/service_form.html', form=form, title='Edit Service', service=service)


@admin.route('/services/delete/<int:service_id>', methods=['POST'])
@login_required
@admin_required
def delete_service(service_id):
    service = Service.query.get_or_404(service_id)
    if service.image_path:
        from flask import current_app
        image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], service.image_path)
        if os.path.exists(image_path):
            os.remove(image_path)
    db.session.delete(service)
    db.session.commit()
    flash('Service deleted.', 'success')
    return redirect(url_for('admin.manage_services'))
