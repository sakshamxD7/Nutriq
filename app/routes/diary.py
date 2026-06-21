from flask import Blueprint, render_template, redirect, url_for, flash, Response
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta, time
from collections import defaultdict, Counter
from app.models.food import FoodLog, FoodItem
from app.extensions import db
import csv
import io

diary_bp = Blueprint('diary', __name__)

@diary_bp.route('/')
@login_required
def index():
    # Fetch food logs for the past 30 days
    today = date.today()
    start_date = today - timedelta(days=29)
    start_datetime = datetime.combine(start_date, time.min)
    
    logs = FoodLog.query.filter(
        FoodLog.user_id == current_user.id,
        FoodLog.logged_at >= start_datetime
    ).order_by(FoodLog.logged_at.asc()).all()
    
    # Group logs by date
    daily_data = defaultdict(lambda: {
        'calories': 0.0,
        'protein': 0.0,
        'carbs': 0.0,
        'fat': 0.0,
        'logs': [],
        'color': 'green' # green, amber, red
    })
    
    # Initialize all 30 days to ensure we have a complete calendar
    target = current_user.daily_calorie_target()
    for i in range(30):
        day = start_date + timedelta(days=i)
        day_str = day.isoformat()
        # Set default values
        daily_data[day_str]['date_display'] = day.strftime("%d %b")
        daily_data[day_str]['day_name'] = day.strftime("%a")
        # Color for 0 calories (under target is green or gray, let's keep green/gray)
        daily_data[day_str]['color'] = 'sage' # organic Sage color for empty

    for log in logs:
        log_date_str = log.logged_at.date().isoformat()
        daily_data[log_date_str]['calories'] += log.calories
        daily_data[log_date_str]['protein'] += log.protein
        daily_data[log_date_str]['carbs'] += log.carbs
        daily_data[log_date_str]['fat'] += log.fat
        daily_data[log_date_str]['logs'].append({
            'id': log.id,
            'name': log.food_item.name,
            'name_hindi': log.food_item.name_hindi or '',
            'meal_type': log.meal_type.capitalize(),
            'quantity': int(log.quantity_grams),
            'calories': int(log.calories),
            'protein': round(log.protein, 1),
            'carbs': round(log.carbs, 1),
            'fat': round(log.fat, 1),
            'note': log.note or ''
        })

    # Color thresholding logic
    # Under (<90%), Near (90% - 110%), Over (>110%)
    for day_str, info in daily_data.items():
        c = info['calories']
        if c == 0:
            info['color'] = 'sage' # Sage / inactive
        elif c < target * 0.90:
            info['color'] = 'green' # Green / Under target
        elif c <= target * 1.10:
            info['color'] = 'amber' # Amber / Perfect or Near target
        else:
            info['color'] = 'red' # Red / Over target

    # Convert to standard sorted list for Jinja
    calendar_days = []
    for i in range(30):
        day_str = (start_date + timedelta(days=i)).isoformat()
        day_info = daily_data[day_str]
        day_info['date_str'] = day_str
        day_info['calories'] = int(day_info['calories'])
        day_info['protein'] = int(day_info['protein'])
        day_info['carbs'] = int(day_info['carbs'])
        day_info['fat'] = int(day_info['fat'])
        calendar_days.append(day_info)

    # Weekly/Monthly summary calculations
    active_days_calories = [d['calories'] for d in calendar_days if d['calories'] > 0]
    avg_calories = sum(active_days_calories) / len(active_days_calories) if active_days_calories else 0
    
    # Most logged foods
    all_food_names = [log.food_item.name for log in logs]
    food_counts = Counter(all_food_names)
    most_common_foods = [food for food, count in food_counts.most_common(3)]
    
    # Best/Worst days
    best_day = None
    worst_day = None
    best_diff = float('inf')
    worst_diff = -1.0
    
    for day_str, info in daily_data.items():
        c = info['calories']
        if c > 0:
            diff = abs(c - target)
            if diff < best_diff:
                best_diff = diff
                best_day = datetime.strptime(day_str, "%Y-%m-%d").strftime("%d %b")
            
            if diff > worst_diff:
                worst_diff = diff
                worst_day = datetime.strptime(day_str, "%Y-%m-%d").strftime("%d %b")

    return render_template(
        'diary/index.html',
        calendar_days=calendar_days,
        avg_calories=int(avg_calories),
        most_common_foods=most_common_foods,
        best_day=best_day or 'N/A',
        worst_day=worst_day or 'N/A',
        target_calories=target
    )

@diary_bp.route('/export')
@login_required
def export():
    # Fetch all user food logs
    logs = FoodLog.query.filter_by(user_id=current_user.id).order_by(FoodLog.logged_at.desc()).all()
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header row
    writer.writerow([
        'Date', 'Meal Type', 'Food Item Name', 'Hindi Name', 
        'Quantity (g)', 'Calories', 'Protein (g)', 'Carbohydrates (g)', 'Fat (g)', 'Note'
    ])
    
    for log in logs:
        writer.writerow([
            log.logged_at.strftime('%Y-%m-%d %H:%M:%S'),
            log.meal_type.capitalize(),
            log.food_item.name,
            log.food_item.name_hindi or '',
            log.quantity_grams,
            round(log.calories, 1),
            round(log.protein, 1),
            round(log.carbs, 1),
            round(log.fat, 1),
            log.note or ''
        ])
        
    output.seek(0)
    
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename=nutriq_diary_{date.today().isoformat()}.csv"}
    )
