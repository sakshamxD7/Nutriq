from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, FloatField, SelectField
from wtforms.validators import DataRequired, Email, Length, NumberRange, ValidationError
from functools import wraps
from app.models.user import User
from app.extensions import db

auth_bp = Blueprint('auth', __name__)

# Premium gate decorator
def premium_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if not current_user.is_premium:
            flash("This feature requires a Nutriq Plus or Pro subscription.", "warning")
            return redirect(url_for('billing.plans'))
        return f(*args, **kwargs)
    return decorated_function


# Forms Definition
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('LOG IN')

class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    age = IntegerField('Age', validators=[DataRequired(), NumberRange(min=1, max=120)])
    gender = SelectField('Gender', choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], validators=[DataRequired()])
    height_cm = FloatField('Height (cm)', validators=[DataRequired(), NumberRange(min=50, max=250)])
    weight_kg = FloatField('Weight (kg)', validators=[DataRequired(), NumberRange(min=10, max=300)])
    activity_level = SelectField('Activity Level', choices=[
        ('sedentary', 'Sedentary (Little/no exercise)'),
        ('light', 'Light (1-3 days/week)'),
        ('moderate', 'Moderate (3-5 days/week)'),
        ('active', 'Active (6-7 days/week)')
    ], validators=[DataRequired()])
    goal = SelectField('Goal', choices=[
        ('lose', 'Lose Weight (Deficit)'),
        ('maintain', 'Maintain Weight'),
        ('gain', 'Gain Weight (Surplus)')
    ], validators=[DataRequired()])
    dietary_pref = SelectField('Dietary Preference', choices=[
        ('veg', 'Vegetarian'),
        ('nonveg', 'Non-Vegetarian'),
        ('vegan', 'Vegan'),
        ('jain', 'Jain')
    ], validators=[DataRequired()])
    submit = SubmitField('GET STARTED')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please login.')


# Routes
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            name=form.name.data,
            email=form.email.data,
            age=form.age.data,
            gender=form.gender.data,
            height_cm=form.height_cm.data,
            weight_kg=form.weight_kg.data,
            activity_level=form.activity_level.data,
            goal=form.goal.data,
            dietary_pref=form.dietary_pref.data
        )
        user.set_password(form.password.data)
        
        # Save to DB
        db.session.add(user)
        db.session.commit()
        
        # Log User In
        login_user(user)
        flash('Account created successfully! Welcome to Nutriq.', 'success')
        return redirect(url_for('dashboard.index'))
        
    return render_template('auth/register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
        
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash(f'Welcome back, {user.name}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard.index'))
        else:
            flash('Invalid email or password.', 'danger')
            
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
