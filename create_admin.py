from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # চেক করছি অ্যাডমিন আগে থেকেই আছে কি না
    admin = User.query.filter_by(email='admin@hotel.com').first()
    
    if not admin:
        new_admin = User(
            username='admin',
            email='admin@hotel.com',
            password_hash=generate_password_hash('admin123'),
            full_name='Hotel Administrator',
            role='admin'
        )
        db.session.add(new_admin)
        db.session.commit()
        print("✅ Admin created successfully!")
    else:
        # যদি থাকে তবে পাসওয়ার্ড আপডেট করে দিচ্ছি
        admin.password_hash = generate_password_hash('admin123')
        db.session.commit()
        print("✅ Admin password updated to 'admin123'!")