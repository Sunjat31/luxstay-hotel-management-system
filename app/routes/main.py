from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from datetime import date
from app import db
from app.models import Room, RoomType, Booking, Service
from app.forms import BookingForm, SearchForm, ImageUploadForm
import os
from werkzeug.utils import secure_filename

main = Blueprint('main', __name__)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}


@main.route('/upload-pool-image', methods=['GET', 'POST'])
@login_required
def upload_pool_image():
    if not current_user.is_admin():
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('main.index'))
    
    form = ImageUploadForm()
    if form.validate_on_submit():
        file = form.image.data
        if file and allowed_file(file.filename):
            filename = secure_filename('pool.jpg')
            file_path = os.path.join('app', 'static', 'img', filename)
            file.save(file_path)
            flash('Pool image uploaded successfully!', 'success')
            return redirect(url_for('main.swimming_health'))
        else:
            flash('Invalid file type. Please upload a JPG, PNG, or GIF image.', 'danger')
    
    return render_template('upload_image.html', form=form, title='Upload Pool Image', feature='Swimming Pool')


@main.route('/upload-sauna-image', methods=['GET', 'POST'])
@login_required
def upload_sauna_image():
    if not current_user.is_admin():
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('main.index'))
    
    form = ImageUploadForm()
    if form.validate_on_submit():
        file = form.image.data
        if file and allowed_file(file.filename):
            filename = secure_filename('sauna.jpg')
            file_path = os.path.join('app', 'static', 'img', filename)
            file.save(file_path)
            flash('Sauna image uploaded successfully!', 'success')
            return redirect(url_for('main.swimming_health'))
        else:
            flash('Invalid file type. Please upload a JPG, PNG, or GIF image.', 'danger')
    
    return render_template('upload_image.html', form=form, title='Upload Sauna Image', feature='Sauna & Steam Bath')


@main.route('/upload-gym-image', methods=['GET', 'POST'])
@login_required
def upload_gym_image():
    if not current_user.is_admin():
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('main.index'))
    
    form = ImageUploadForm()
    if form.validate_on_submit():
        file = form.image.data
        if file and allowed_file(file.filename):
            filename = secure_filename('gym.jpg')
            file_path = os.path.join('app', 'static', 'img', filename)
            file.save(file_path)
            flash('Gym image uploaded successfully!', 'success')
            return redirect(url_for('main.swimming_health'))
        else:
            flash('Invalid file type. Please upload a JPG, PNG, or GIF image.', 'danger')
    
    return render_template('upload_image.html', form=form, title='Upload Gym Image', feature='Gym')


@main.route('/', methods=['GET', 'POST'])
def index():
    form = SearchForm()
    room_types = RoomType.query.all()
    form.room_type.choices = [(0, 'All Types')] + [(rt.id, rt.name) for rt in room_types]

    rooms = Room.query.filter_by(status='available').all()
    stats = {
        'total_rooms': Room.query.count(),
        'available': Room.query.filter_by(status='available').count(),
        'occupied': Room.query.filter_by(status='occupied').count(),
        'room_types': len(room_types)
    }

    if form.validate_on_submit():
        query = Room.query.filter_by(status='available')
        if form.room_type.data and form.room_type.data != 0:
            query = query.filter_by(room_type_id=form.room_type.data)
        if form.guests.data:
            query = query.filter(Room.capacity >= form.guests.data)
        rooms = query.all()

    return render_template('index.html', rooms=rooms, form=form,
                           room_types=room_types, stats=stats)


@main.route('/rooms')
def rooms():
    room_type_filter = request.args.get('type', 0, type=int)
    status_filter = request.args.get('status', 'available')

    query = Room.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    if room_type_filter:
        query = query.filter_by(room_type_id=room_type_filter)

    rooms = query.all()
    room_types = RoomType.query.all()
    return render_template('rooms.html', rooms=rooms, room_types=room_types,
                           selected_type=room_type_filter, selected_status=status_filter)


@main.route('/book/<int:room_id>', methods=['GET', 'POST'])
@login_required
def book_room(room_id):
    room = Room.query.get_or_404(room_id)
    if room.status != 'available':
        flash('This room is not available for booking.', 'danger')
        return redirect(url_for('main.rooms'))

    form = BookingForm()
    form.room_id.choices = [(room.id, f'Room {room.room_number}')]

    if form.validate_on_submit():
        if form.check_in.data >= form.check_out.data:
            flash('Check-out date must be after check-in date.', 'danger')
            return render_template('book.html', form=form, room=room)

        if form.check_in.data < date.today():
            flash('Check-in date cannot be in the past.', 'danger')
            return render_template('book.html', form=form, room=room)

        nights = (form.check_out.data - form.check_in.data).days
        total = float(room.room_type.base_price) * nights

        booking = Booking(
            user_id=current_user.id,
            room_id=room.id,
            check_in=form.check_in.data,
            check_out=form.check_out.data,
            guests=form.guests.data,
            total_amount=total,
            special_requests=form.special_requests.data,
            status='confirmed'
        )
        room.status = 'reserved'
        db.session.add(booking)
        db.session.commit()

        flash(f'Booking confirmed! Total amount: {total:,.2f} BDT for {nights} night(s).', 'success')
        return redirect(url_for('main.my_bookings'))

    return render_template('book.html', form=form, room=room)


@main.route('/my-bookings')
@login_required
def my_bookings():
    bookings = Booking.query.filter_by(user_id=current_user.id)\
                            .order_by(Booking.created_at.desc()).all()
    return render_template('my_bookings.html', bookings=bookings)


@main.route('/cancel-booking/<int:booking_id>', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != current_user.id and not current_user.is_admin():
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('main.my_bookings'))

    if booking.status in ('confirmed', 'reserved'):
        booking.status = 'cancelled'
        booking.room.status = 'available'
        db.session.commit()
        flash('Booking cancelled successfully.', 'success')
    else:
        flash('This booking cannot be cancelled.', 'warning')

    return redirect(url_for('main.my_bookings'))


@main.route('/meetings-events')
def meetings_events():
    return render_template('meetings_events.html')


@main.route('/eat-drink')
def eat_drink():
    return render_template('eat_drink.html')


@main.route('/swimming-health')
def swimming_health():
    services = Service.query.filter_by(category='health').all()
    return render_template('swimming_health.html', services=services)


@main.route('/about')
def about():
    return render_template('about.html')


@main.route('/payment')
@login_required
def payment():
    return render_template('payment.html')
