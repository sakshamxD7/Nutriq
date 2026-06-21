import requests
from app.models.food import FoodItem
from app.extensions import db

def lookup_barcode(barcode):
    """
    Looks up a product in the Open Food Facts API by barcode.
    If found, returns the parsed nutrient details and caches it in the FoodItem table.
    """
    if not barcode:
        return None

    # Check database cache first
    cached_food = FoodItem.query.filter_by(barcode=barcode).first()
    if cached_food:
        return cached_food

    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    headers = {
        'User-Agent': 'Nutriq Calorie Tracker - Python/Flask WebApp - Version 1.0'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == 1:
                product = data.get("product", {})
                
                # Extract details
                name = product.get("product_name") or product.get("product_name_en") or f"Packaged Food ({barcode})"
                nutriments = product.get("nutriments", {})
                
                # Fetch calories per 100g, fallback options
                calories = nutriments.get("energy-kcal_100g")
                if calories is None:
                    # If energy is in kJ, convert to kcal
                    energy_kj = nutriments.get("energy_100g")
                    if energy_kj is not None:
                        calories = energy_kj / 4.184
                    else:
                        calories = 0.0
                
                protein = nutriments.get("proteins_100g", 0.0)
                carbs = nutriments.get("carbohydrates_100g", 0.0)
                fat = nutriments.get("fat_100g", 0.0)
                fiber = nutriments.get("fiber_100g", 0.0)

                # Save new food item to the DB cache
                new_food = FoodItem(
                    name=name,
                    category="Packaged",
                    calories_per_100g=float(calories),
                    protein_g=float(protein),
                    carbs_g=float(carbs),
                    fat_g=float(fat),
                    fiber_g=float(fiber),
                    is_verified=True,
                    source="openfoodfacts",
                    barcode=barcode
                )
                
                db.session.add(new_food)
                db.session.commit()
                return new_food
    except Exception as e:
        print(f"Barcode service lookup error: {str(e)}")
        
    return None
