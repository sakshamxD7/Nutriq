from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.food import FoodItem, FoodLog
from app.services.food_db import search_food_items, get_food_by_id
from app.services.barcode import lookup_barcode
from app.extensions import db
from datetime import datetime

food_bp = Blueprint('food', __name__)

@food_bp.route('/search', methods=['GET'])
@login_required
def search():
    query = request.args.get('q', '')
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.args.get('format') == 'json':
        results = search_food_items(query)
        # Serialize to JSON
        return jsonify([{
            'id': item.id,
            'name': item.name,
            'name_hindi': item.name_hindi or '',
            'category': item.category,
            'calories_per_100g': item.calories_per_100g,
            'protein_g': item.protein_g,
            'carbs_g': item.carbs_g,
            'fat_g': item.fat_g,
            'fiber_g': item.fiber_g,
            'region': item.region or ''
        } for item in results])
        
    return render_template('food/search.html', query=query)


@food_bp.route('/log', methods=['GET', 'POST'])
@login_required
def log():
    if request.method == 'POST':
        food_id = request.form.get('food_item_id')
        meal_type = request.form.get('meal_type')
        quantity = request.form.get('quantity_grams')
        note = request.form.get('note', '')

        if not food_id or not meal_type or not quantity:
            flash("All fields (food, meal type, quantity) are required.", "danger")
            return redirect(url_for('dashboard.index'))
            
        try:
            food_item = get_food_by_id(int(food_id))
            if not food_item:
                flash("Food item not found.", "danger")
                return redirect(url_for('dashboard.index'))

            new_log = FoodLog(
                user_id=current_user.id,
                food_item_id=food_item.id,
                meal_type=meal_type,
                quantity_grams=float(quantity),
                note=note,
                logged_at=datetime.utcnow()
            )
            db.session.add(new_log)
            db.session.commit()
            flash(f"Successfully logged {quantity}g of {food_item.name} for {meal_type.capitalize()}.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error logging food: {str(e)}", "danger")

        return redirect(url_for('dashboard.index'))

    # If GET, render a logging form (optionally preloaded with a food item)
    food_id = request.args.get('food_item_id')
    food_item = get_food_by_id(int(food_id)) if food_id else None
    return render_template('food/log.html', food_item=food_item)


@food_bp.route('/barcode', methods=['GET'])
@login_required
def barcode_scanner():
    return render_template('food/barcode.html')


@food_bp.route('/barcode/lookup', methods=['POST'])
@login_required
def barcode_lookup():
    data = request.get_json() or {}
    barcode = data.get('barcode')
    
    if not barcode:
        return jsonify({'error': 'No barcode provided'}), 400
        
    food_item = lookup_barcode(barcode)
    if food_item:
        return jsonify({
            'id': food_item.id,
            'name': food_item.name,
            'category': food_item.category,
            'calories_per_100g': food_item.calories_per_100g,
            'protein_g': food_item.protein_g,
            'carbs_g': food_item.carbs_g,
            'fat_g': food_item.fat_g,
            'fiber_g': food_item.fiber_g,
        })
    else:
        return jsonify({'error': 'Product not found or Open Food Facts API offline'}), 404


@food_bp.route('/delete/<int:log_id>', methods=['POST'])
@login_required
def delete_log(log_id):
    log_entry = FoodLog.query.filter_by(id=log_id, user_id=current_user.id).first()
    if log_entry and log_entry.user_id == current_user.id:
        try:
            food_name = log_entry.food_item.name
            db.session.delete(log_entry)
            db.session.commit()
            flash(f"Deleted log entry for {food_name}.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error deleting entry: {str(e)}", "danger")
    else:
        flash("Log entry not found or unauthorized.", "danger")
        
    # Redirect back to referring page or dashboard
    ref = request.referrer or url_for('dashboard.index')
    return redirect(ref)
