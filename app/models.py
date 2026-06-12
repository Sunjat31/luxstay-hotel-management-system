from datetime import datetime
from flask_login import UserMixin
from app import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(20))
    role = db.Column(db.String(20), default='guest')  # 'admin' or 'guest'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    bookings = db.relationship('Booking', backref='guest', lazy=True)

    def is_admin(self):
        return self.role == 'admin'

    def __repr__(self):
        return f'<User {self.username}>'


class RoomType(db.Model):
    __tablename__ = 'room_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    base_price = db.Column(db.Numeric(10, 2), nullable=False)
    rooms = db.relationship('Room', backref='room_type', lazy=True)

    def __repr__(self):
        return f'<RoomType {self.name}>'


class Room(db.Model):
    __tablename__ = 'rooms'
    id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.String(10), unique=True, nullable=False)
    floor = db.Column(db.Integer, nullable=False)
    room_type_id = db.Column(db.Integer, db.ForeignKey('room_types.id'), nullable=False)
    status = db.Column(db.String(20), default='available')  # available, occupied, maintenance, reserved
    capacity = db.Column(db.Integer, default=2)
    amenities = db.Column(db.Text)
    bookings = db.relationship('Booking', backref='room', lazy=True)

    def __repr__(self):
        return f'<Room {self.room_number}>'


class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    check_in = db.Column(db.Date, nullable=False)
    check_out = db.Column(db.Date, nullable=False)
    guests = db.Column(db.Integer, default=1)
    status = db.Column(db.String(20), default='confirmed')  # confirmed, checked_in, checked_out, cancelled
    total_amount = db.Column(db.Numeric(10, 2))
    special_requests = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    payment = db.relationship('Payment', backref='booking', uselist=False)

    def nights(self):
        return (self.check_out - self.check_in).days

    def __repr__(self):
        return f'<Booking {self.id}>'


class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), unique=True, nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    method = db.Column(db.String(50))  # cash, card, bkash, nagad
    status = db.Column(db.String(20), default='pending')  # pending, paid, refunded
    transaction_id = db.Column(db.String(100))
    paid_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Payment {self.id}>'


class Staff(db.Model):
    __tablename__ = 'staff'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    position = db.Column(db.String(100))
    department = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    salary = db.Column(db.Numeric(10, 2))
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Staff {self.full_name}>'


class Service(db.Model):
    __tablename__ = 'services'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    image_path = db.Column(db.String(200))  # path to uploaded image
    category = db.Column(db.String(50), default='health')  # health, dining, etc.
    features = db.Column(db.Text)  # comma-separated features
    icon_class = db.Column(db.String(50))  # fontawesome icon class

    def __repr__(self):
        return f'<Service {self.name}>'
