from datetime import datetime
from app.extensions import db

class DietPlan(db.Model):
    __tablename__ = 'diet_plans'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    content_json = db.Column(db.Text, nullable=False) # Stores JSON string
    generated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_active = db.Column(db.Boolean, default=True)


class Subscription(db.Model):
    __tablename__ = 'subscriptions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    stripe_customer_id = db.Column(db.String(100), nullable=True)
    stripe_subscription_id = db.Column(db.String(100), nullable=True, unique=True)
    plan_type = db.Column(db.String(20), default="free") # free/plus/pro
    status = db.Column(db.String(20), default="active") # active/cancelled/past_due
    current_period_end = db.Column(db.DateTime, nullable=True)


class WeightLog(db.Model):
    __tablename__ = 'weight_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    weight_kg = db.Column(db.Float, nullable=False)
    logged_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
