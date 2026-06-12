from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, SubmitField, SelectField,
                     IntegerField, DateField, TextAreaField, DecimalField, BooleanField, FileField)
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, NumberRange
from flask_wtf.file import FileAllowed, FileRequired
from datetime import date


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class RegistrationForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=150)])
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')


class BookingForm(FlaskForm):
    room_id = SelectField('Room', coerce=int, validators=[DataRequired()])
    check_in = DateField('Check-in Date', validators=[DataRequired()])
    check_out = DateField('Check-out Date', validators=[DataRequired()])
    guests = IntegerField('Number of Guests', validators=[DataRequired(), NumberRange(min=1, max=10)])
    special_requests = TextAreaField('Special Requests', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Book Now')


class RoomForm(FlaskForm):
    room_number = StringField('Room Number', validators=[DataRequired(), Length(max=10)])
    floor = IntegerField('Floor', validators=[DataRequired(), NumberRange(min=1)])
    room_type_id = SelectField('Room Type', coerce=int, validators=[DataRequired()])
    status = SelectField('Status', choices=[
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('maintenance', 'Maintenance'),
        ('reserved', 'Reserved')
    ])
    capacity = IntegerField('Capacity', validators=[DataRequired(), NumberRange(min=1, max=20)])
    amenities = TextAreaField('Amenities', validators=[Optional()])
    submit = SubmitField('Save Room')


class RoomTypeForm(FlaskForm):
    name = StringField('Type Name', validators=[DataRequired(), Length(max=50)])
    description = TextAreaField('Description', validators=[Optional()])
    base_price = DecimalField('Base Price (BDT)', places=2, validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Save Room Type')


class StaffForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=150)])
    position = StringField('Position', validators=[Optional(), Length(max=100)])
    department = StringField('Department', validators=[Optional(), Length(max=100)])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])
    email = StringField('Email', validators=[Optional(), Email()])
    salary = DecimalField('Salary (BDT)', places=2, validators=[Optional(), NumberRange(min=0)])
    submit = SubmitField('Save Staff')


class ServiceForm(FlaskForm):
    name = StringField('Service Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional()])
    image = FileField('Image', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')])
    category = StringField('Category', validators=[Optional(), Length(max=50)], default='health')
    features = TextAreaField('Features (comma-separated)', validators=[Optional()])
    icon_class = StringField('Icon Class (FontAwesome)', validators=[Optional(), Length(max=50)])
    submit = SubmitField('Save Service')


class SearchForm(FlaskForm):
    check_in = DateField('Check-in', validators=[Optional()])
    check_out = DateField('Check-out', validators=[Optional()])
    room_type = SelectField('Room Type', coerce=int, choices=[(0, 'All Types')], validators=[Optional()])
    guests = IntegerField('Guests', validators=[Optional(), NumberRange(min=1)], default=1)
    submit = SubmitField('Search')


class ImageUploadForm(FlaskForm):
    image = FileField('Image', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    submit = SubmitField('Upload Image')
