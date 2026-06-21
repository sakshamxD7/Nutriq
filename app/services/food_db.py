from app.models.food import FoodItem
from app.extensions import db

def search_food_items(query, category=None):
    """
    Search database using a fuzzy match against name and name_hindi.
    Optional filter by category.
    """
    if not query:
        return []
    
    search_pattern = f"%{query}%"
    
    # Simple case-insensitive search matching English name or Hindi name
    filters = [
        (FoodItem.name.ilike(search_pattern)) | 
        (FoodItem.name_hindi.ilike(search_pattern))
    ]
    
    if category:
        filters.append(FoodItem.category == category)
        
    return FoodItem.query.filter(*filters).all()

def get_food_by_id(food_id):
    """Retrieve food item by primary key."""
    return FoodItem.query.get(food_id)
