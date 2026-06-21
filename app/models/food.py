from datetime import datetime
from app.extensions import db

class FoodItem(db.Model):
    __tablename__ = 'food_items'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, index=True)
    name_hindi = db.Column(db.String(150), nullable=True)
    category = db.Column(db.String(50), default="Indian") # Indian/Global/Packaged
    calories_per_100g = db.Column(db.Float, nullable=False)
    protein_g = db.Column(db.Float, default=0.0)
    carbs_g = db.Column(db.Float, default=0.0)
    fat_g = db.Column(db.Float, default=0.0)
    fiber_g = db.Column(db.Float, default=0.0)
    region = db.Column(db.String(100), nullable=True) # Punjab, South India, etc.
    is_verified = db.Column(db.Boolean, default=False)
    source = db.Column(db.String(50), default="manual") # manual/openfoodfacts/usda
    barcode = db.Column(db.String(50), nullable=True, unique=True, index=True) # Barcode for lookup

    # Relationships
    logs = db.relationship('FoodLog', backref='food_item', lazy=True, cascade="all, delete-orphan")


class FoodLog(db.Model):
    __tablename__ = 'food_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    food_item_id = db.Column(db.Integer, db.ForeignKey('food_items.id', ondelete='CASCADE'), nullable=False)
    meal_type = db.Column(db.String(20), nullable=False) # breakfast/lunch/dinner/snacks
    quantity_grams = db.Column(db.Float, nullable=False)
    logged_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    note = db.Column(db.String(250), nullable=True)

    @property
    def calories(self):
        return (self.quantity_grams / 100.0) * self.food_item.calories_per_100g

    @property
    def protein(self):
        return (self.quantity_grams / 100.0) * self.food_item.protein_g

    @property
    def carbs(self):
        return (self.quantity_grams / 100.0) * self.food_item.carbs_g

    @property
    def fat(self):
        return (self.quantity_grams / 100.0) * self.food_item.fat_g

    @property
    def fiber(self):
        return (self.quantity_grams / 100.0) * self.food_item.fiber_g
