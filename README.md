# 🏨 LuxStay — Smart Hotel Management System

A full-stack Flask web application with MySQL DBMS integration for managing a luxury hotel.

---

## 📁 Project Structure
```
hotel_system/
├── app/                  # Main application package
│   ├── __init__.py       # App factory & blueprint registration
│   ├── models.py         # SQLAlchemy ORM models
│   ├── forms.py          # Flask-WTF forms
│   ├── routes/
│   │   ├── main.py       # Home, rooms, booking routes
│   │   ├── auth.py       # Login, register, logout
│   │   └── admin.py      # Admin dashboard & management
│   ├── static/
│   │   ├── css/style.css # Luxury UI styles
│   │   └── js/script.js  # Client-side interactivity
│   └── templates/        # Jinja2 HTML templates
├── database/
│   └── hotel_db.sql      # MySQL schema + stored procedures
├── .env                  # Environment variables (edit this!)
├── config.py             # App configuration
├── requirements.txt      # Python dependencies
└── run.py                # Entry point
```

---

## ⚙️ Setup Instructions

### 1. Prerequisites
- Python 3.10+
- MySQL Server 8.0+
- pip

### 2. Create MySQL Database
```sql
CREATE DATABASE hotel_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```
Then import the schema:
```bash
mysql -u root -p hotel_db < database/hotel_db.sql
```

### 3. Configure Environment
Edit `.env` file:
```env
SECRET_KEY=sunjat-this-to-a-random-string
DB_USER=root
DB_PASSWORD=sun@#5701418@
DB_HOST=localhost
DB_PORT=3306
DB_NAME=hotel_db
```

### 4. Install Dependencies
```bash
cd hotel_system
pip install -r requirements.txt
```

### 5. Run the Application
```bash
python run.py
```
Open: **http://localhost:5000**

---

## 🔑 Default Credentials

| Role  | Email              | Password  |
|-------|--------------------|-----------|
| Admin | admin@hotel.com    | admin123  |

> ⚠️ Change admin password in production!

---

## ✨ Features

### Guest Features
- Browse available rooms with filters
- Search by room type, dates, and guest count
- Online room booking
- View and cancel bookings
- User registration and login

### Admin Features
- Dashboard with live statistics
- Room management (CRUD)
- Room type management with pricing
- Booking management with status updates
- Guest user management
- Staff management

---

## 🗄️ Database Models

| Table        | Description                          |
|--------------|--------------------------------------|
| `users`      | Guest and admin accounts             |
| `room_types` | Room categories with base pricing    |
| `rooms`      | Individual hotel rooms               |
| `bookings`   | Guest reservations                   |
| `payments`   | Payment records per booking          |
| `staff`      | Hotel staff records                  |

---

## 🛠️ Tech Stack

| Layer      | Technology                  |
|------------|-----------------------------|
| Backend    | Python 3 + Flask            |
| ORM        | SQLAlchemy (Flask-SQLAlchemy)|
| Database   | MySQL 8.0 (via PyMySQL)     |
| Auth       | Flask-Login                 |
| Forms      | Flask-WTF + WTForms         |
| Frontend   | HTML5, CSS3, Vanilla JS     |
| Templating | Jinja2                      |
| Icons      | Font Awesome 6              |

---

## 📌 Notes

- The app auto-seeds rooms and admin user on first run
- CSRF protection is enabled on all forms
- Passwords are hashed with Werkzeug's `scrypt`
- Admin panel is protected by role-based access control
