from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'


def create_app(config_name='default'):
    # Set up static folder paths
    import os
    app_dir = os.path.dirname(os.path.abspath(__file__))
    static_dir = os.path.join(app_dir, 'static')
    
    app = Flask(__name__, static_folder=static_dir, static_url_path='/static')
    app.config.from_object(config[config_name])

    db.init_app(app)
    login_manager.init_app(app)

    from app.routes.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from app.routes.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from app.routes.admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    with app.app_context():
        db.create_all()
        _seed_data()

    return app


def _seed_data():
    """Seed initial data if tables are empty."""
    from app.models import User, Room, RoomType, Service
    from werkzeug.security import generate_password_hash

    # Create admin user
    if not User.query.filter_by(email='admin@hotel.com').first():
        admin = User(
            username='admin',
            email='admin@hotel.com',
            password_hash=generate_password_hash('admin123'),
            role='admin',
            full_name='Hotel Administrator',
            phone='01700000000'
        )
        db.session.add(admin)

    # Seed room types
    if RoomType.query.count() == 0:
        types = [
            RoomType(name='Standard', description='Comfortable standard room', base_price=2500.00),
            RoomType(name='Deluxe', description='Spacious deluxe room with city view', base_price=4500.00),
            RoomType(name='Suite', description='Luxury suite with premium amenities', base_price=8000.00),
            RoomType(name='Presidential', description='Presidential suite — the pinnacle of luxury', base_price=15000.00),
        ]
        db.session.add_all(types)
        db.session.flush()

    # Seed rooms
    if Room.query.count() == 0:
        rt = {rt.name: rt for rt in RoomType.query.all()}
        rooms = [
            Room(room_number='101', floor=1, room_type_id=rt['Standard'].id, status='available', capacity=2, amenities='AC, TV, WiFi, Attached Bathroom'),
            Room(room_number='102', floor=1, room_type_id=rt['Standard'].id, status='available', capacity=2, amenities='AC, TV, WiFi, Attached Bathroom'),
            Room(room_number='201', floor=2, room_type_id=rt['Deluxe'].id, status='available', capacity=3, amenities='AC, Smart TV, WiFi, Mini Bar, City View'),
            Room(room_number='202', floor=2, room_type_id=rt['Deluxe'].id, status='occupied', capacity=3, amenities='AC, Smart TV, WiFi, Mini Bar, City View'),
            Room(room_number='301', floor=3, room_type_id=rt['Suite'].id, status='available', capacity=4, amenities='AC, Smart TV, WiFi, Jacuzzi, Living Room, Mini Bar'),
            Room(room_number='401', floor=4, room_type_id=rt['Presidential'].id, status='available', capacity=6, amenities='Full Suite, Private Pool, Butler Service, All Amenities'),
        ]
        db.session.add_all(rooms)

    # Seed services
    if Service.query.count() == 0:
        services = [
            Service(name='Swimming Pool', description='Relax in our temperature-controlled outdoor pool with stunning views and comfortable lounging areas.', category='health', features='Temperature controlled,Outdoor pool,Lifeguard on duty,Poolside service', icon_class='fas fa-swimmer'),
            Service(name='Sauna & Steam Bath', description='Detoxify and relax in our traditional sauna and modern steam bath facilities.', category='health', features='Finnish sauna,Steam bath,Aromatherapy,Relaxation areas', icon_class='fas fa-hot-tub'),
            Service(name='Gym', description='Stay fit with our fully equipped fitness center featuring modern equipment and personal training options.', category='health', features='Cardio equipment,Free weights,Personal training,Group classes', icon_class='fas fa-dumbbell'),
            Service(name='Billiard', description='Enjoy recreational games in our billiard room with professional tables and a relaxed atmosphere.', category='health', features='Professional tables,Game instruction,Tournament hosting,Refreshment service', icon_class='fas fa-table-tennis'),
        ]
        db.session.add_all(services)

    db.session.commit()
