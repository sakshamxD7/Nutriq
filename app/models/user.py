from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db, login_manager

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(200), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False) # male/female/other
    height_cm = db.Column(db.Float, nullable=False)
    weight_kg = db.Column(db.Float, nullable=False)
    activity_level = db.Column(db.String(20), nullable=False) # sedentary/light/moderate/active
    goal = db.Column(db.String(20), nullable=False) # lose/maintain/gain
    dietary_pref = db.Column(db.String(20), nullable=False) # veg/nonveg/vegan/jain
    is_premium = db.Column(db.Boolean, default=False)
    reminder_time = db.Column(db.String(5), default="08:00") # Time formatted as HH:MM
    email_reminders = db.Column(db.Boolean, default=True) # Toggle reminders on/off
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    food_logs = db.relationship('FoodLog', backref='user', lazy=True, cascade="all, delete-orphan")
    diet_plans = db.relationship('DietPlan', backref='user', lazy=True, cascade="all, delete-orphan")
    subscriptions = db.relationship('Subscription', backref='user', lazy=True, cascade="all, delete-orphan")
    weight_logs = db.relationship('WeightLog', backref='user', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def calculate_bmr(self):
        """Calculate BMR using Mifflin-St Jeor Equation."""
        # BMR = 10 * weight (kg) + 6.25 * height (cm) - 5 * age (y) + s
        # s is +5 for male, -161 for female, and average -78 for other/not specified
        if self.gender.lower() == 'male':
            s = 5
        elif self.gender.lower() == 'female':
            s = -161
        else:
            s = -78
        
        return (10 * self.weight_kg) + (6.25 * self.height_cm) - (5 * self.age) + s

    def calculate_tdee(self):
        """Calculate Total Daily Energy Expenditure."""
        bmr = self.calculate_bmr()
        multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725
        }
        multiplier = multipliers.get(self.activity_level.lower(), 1.2)
        return bmr * multiplier

    def daily_calorie_target(self):
        """Calculate daily calorie intake targets based on user goals."""
        tdee = self.calculate_tdee()
        if self.goal.lower() == 'lose':
            # 500 kcal deficit
            target = tdee - 500
        elif self.goal.lower() == 'gain':
            # 500 kcal surplus
            target = tdee + 500
        else:
            # Maintain
            target = tdee
        
        # Ensure a minimum sensible calorie floor (1200 kcal for safety)
        return max(1200, int(round(target)))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
