from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime, date, time, timedelta
from app.models.food import FoodLog, FoodItem
from app.models.plan import WeightLog
from app.extensions import db

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    # Today's logs
    today = date.today()
    start_of_today = datetime.combine(today, time.min)
    
    today_logs = FoodLog.query.filter(
        FoodLog.user_id == current_user.id,
        FoodLog.logged_at >= start_of_today
    ).all()
    
    # Calculate calorie totals
    total_calories = sum(log.calories for log in today_logs)
    target_calories = current_user.daily_calorie_target()
    
    # Calculate macro breakdown
    total_protein = sum(log.protein for log in today_logs)
    total_carbs = sum(log.carbs for log in today_logs)
    total_fat = sum(log.fat for log in today_logs)
    
    total_macros_weight = total_protein + total_carbs + total_fat
    
    if total_macros_weight > 0:
        protein_pct = (total_protein / total_macros_weight) * 100
        carbs_pct = (total_carbs / total_macros_weight) * 100
        fat_pct = (total_fat / total_macros_weight) * 100
    else:
        protein_pct = carbs_pct = fat_pct = 0.0
        
    # Get last 5 entries
    recent_logs = FoodLog.query.filter_by(user_id=current_user.id).order_by(FoodLog.logged_at.desc()).limit(5).all()

    # Get weight logs (last 7 logs)
    w_logs = WeightLog.query.filter_by(user_id=current_user.id).order_by(WeightLog.logged_at.desc()).limit(7).all()
    w_logs.reverse() # Order by date ascending
    
    # Generate SVG parameters for Weight Chart
    svg_points = ""
    svg_dots = []
    
    if not w_logs:
        # Seed dummy weight log if empty so chart doesn't look empty
        # Use user's baseline weight
        baseline_weight = current_user.weight_kg
        svg_points = f"0,50 100,50 200,50 300,50"
        svg_dots = [
            {"x": 0, "y": 50, "val": baseline_weight, "date": "No Data"},
            {"x": 300, "y": 50, "val": baseline_weight, "date": "No Data"}
        ]
    else:
        # Scale coordinates: X from 20 to 280, Y from 15 to 85
        min_w = min(l.weight_kg for l in w_logs) - 2
        max_w = max(l.weight_kg for l in w_logs) + 2
        w_range = max_w - min_w if max_w != min_w else 1.0
        
        num_logs = len(w_logs)
        points_list = []
        for idx, log in enumerate(w_logs):
            x = 20 + (idx * (260 / (num_logs - 1) if num_logs > 1 else 260))
            y = 85 - ((log.weight_kg - min_w) / w_range) * 70
            points_list.append(f"{x},{y}")
            svg_dots.append({
                "x": x,
                "y": y,
                "val": round(log.weight_kg, 1),
                "date": log.logged_at.strftime("%d %b")
            })
        svg_points = " ".join(points_list)

    # Fetch some default common foods for quick add
    quick_add_foods = {
        'breakfast': FoodItem.query.filter(FoodItem.name.in_(['Idli', 'Poha', 'Aloo Paratha'])).all(),
        'lunch': FoodItem.query.filter(FoodItem.name.in_(['Dal Tadka', 'Plain rice (boiled)', 'Roti (home/restaurant)'])).all(),
        'dinner': FoodItem.query.filter(FoodItem.name.in_(['Paneer Butter Masala', 'Sambar', 'Chicken curry'])).all(),
        'snacks': FoodItem.query.filter(FoodItem.name.in_(['Samosa', 'Chai (with milk)', 'Namkeen mixture'])).all()
    }
    
    # In-app notification banner check
    show_reminder_banner = len(today_logs) == 0

    return render_template(
        'dashboard/index.html',
        first_name=current_user.name.split()[0],
        total_calories=int(total_calories),
        target_calories=target_calories,
        protein_pct=round(protein_pct, 1),
        carbs_pct=round(carbs_pct, 1),
        fat_pct=round(fat_pct, 1),
        protein_g=round(total_protein, 1),
        carbs_g=round(total_carbs, 1),
        fat_g=round(total_fat, 1),
        recent_logs=recent_logs,
        svg_points=svg_points,
        svg_dots=svg_dots,
        quick_add_foods=quick_add_foods,
        show_reminder_banner=show_reminder_banner
    )
