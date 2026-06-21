from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, Response, stream_with_context, session
from flask_login import login_required, current_user
from app.routes.auth import premium_required
from app.services.gemini import generate_diet_plan, chat_response
from app.models.plan import DietPlan
from app.models.food import FoodItem, FoodLog
from app.extensions import db
from datetime import datetime, date, time
import json
import logging

logger = logging.getLogger(__name__)
ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/plan', methods=['GET', 'POST'])
@login_required
@premium_required
def diet_plan():
    active_plan = DietPlan.query.filter_by(user_id=current_user.id, is_active=True).order_by(DietPlan.generated_at.desc()).first()
    plan_data = None
    
    if active_plan:
        try:
            plan_data = json.loads(active_plan.content_json)
        except Exception as e:
            logger.error(f"Error decoding active plan: {str(e)}")

    if request.method == 'POST':
        duration = int(request.form.get('duration', 7))
        cuisine = request.form.get('cuisine', 'Mixed')
        allergies = request.form.get('allergies', '')

        preferences = {
            'duration': duration,
            'cuisine': cuisine,
            'allergies': allergies
        }

        # Call Gemini service to generate plan
        try:
            plan_json = generate_diet_plan(current_user, preferences)
            
            # Deactivate previous plans
            DietPlan.query.filter_by(user_id=current_user.id).update({'is_active': False})
            
            # Save new plan
            new_plan = DietPlan(
                user_id=current_user.id,
                content_json=json.dumps(plan_json),
                generated_at=datetime.utcnow(),
                is_active=True
            )
            db.session.add(new_plan)
            db.session.commit()
            flash("AI Diet Plan generated successfully!", "success")
            return redirect(url_for('ai.diet_plan'))
        except Exception as e:
            db.session.rollback()
            flash(f"Failed to generate diet plan: {str(e)}", "danger")

    return render_template('ai/diet_plan.html', plan_data=plan_data)


@ai_bp.route('/plan/log-meal', methods=['POST'])
@login_required
@premium_required
def log_meal_from_plan():
    """Logs a meal directly from the generated diet plan into the user's daily food logs."""
    meal_name = request.form.get('name')
    meal_type = request.form.get('meal_type') # breakfast/lunch/dinner/snacks
    calories = request.form.get('calories')
    protein = request.form.get('protein')
    carbs = request.form.get('carbs')
    fat = request.form.get('fat')
    quantity = request.form.get('quantity', '1 serving')

    if not meal_name or not meal_type or not calories:
        return jsonify({'success': False, 'error': 'Missing parameters'}), 400

    try:
        # Check if the food item already exists in DB, or create a mock/packaged record for it
        food_item = FoodItem.query.filter_by(name=meal_name).first()
        if not food_item:
            # We treat the serving size as 100g to keep calculation clean
            # calories_per_100g = total_calories / 1 (representing a single serving of 100g)
            food_item = FoodItem(
                name=meal_name,
                category="Indian",
                calories_per_100g=float(calories),
                protein_g=float(protein or 0),
                carbs_g=float(carbs or 0),
                fat_g=float(fat or 0),
                is_verified=True,
                source="manual"
            )
            db.session.add(food_item)
            db.session.commit()

        # Log 100g (equivalent to the full calorie allocation defined by the AI)
        new_log = FoodLog(
            user_id=current_user.id,
            food_item_id=food_item.id,
            meal_type=meal_type.lower(),
            quantity_grams=100.0,
            note=f"AI Generated Meal: {quantity}",
            logged_at=datetime.utcnow()
        )
        db.session.add(new_log)
        db.session.commit()

        return jsonify({'success': True, 'message': f'Logged {meal_name} to your {meal_type.capitalize()}!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_bp.route('/chat', methods=['GET'])
@login_required
@premium_required
def chatbot():
    # Retrieve chat history from session or initialize it
    if 'chat_history' not in session:
        session['chat_history'] = []
    return render_template('ai/chatbot.html')


@ai_bp.route('/chat/message', methods=['POST'])
@login_required
@premium_required
def chat_message():
    user_message = request.form.get('message', '').strip()
    if not user_message:
        return jsonify({'error': 'Message cannot be empty'}), 400

    # Retrieve history
    history = session.get('chat_history', [])
    
    # Restrict session chat history to last 10 messages (5 exchanges)
    if len(history) > 10:
        history = history[-10:]

    # Fetch today's food logs for context
    today = date.today()
    start_of_today = datetime.combine(today, time.min)
    today_logs = FoodLog.query.filter(
        FoodLog.user_id == current_user.id,
        FoodLog.logged_at >= start_of_today
    ).all()

    # Generate streaming SSE response
    def sse_stream():
        full_response_parts = []
        try:
            # Stream from Gemini service
            for chunk in chat_response(current_user, today_logs, history, user_message):
                full_response_parts.append(chunk)
                # Format chunk as an SSE data payload
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            
            # Store new exchange in history
            full_response_text = "".join(full_response_parts)
            history.append({'user': user_message, 'bot': full_response_text})
            session['chat_history'] = history[-10:] # Cap at 10 items
            session.modified = True
            
            # Yield terminal signal
            yield "data: [DONE]\n\n"
        except Exception as e:
            logger.error(f"SSE stream error: {str(e)}")
            yield f"data: {json.dumps({'error': 'Streaming interrupted'})}\n\n"
            yield "data: [DONE]\n\n"

    return Response(stream_with_context(sse_stream()), mimetype="text/event-stream")


@ai_bp.route('/chat/clear', methods=['POST'])
@login_required
@premium_required
def clear_chat():
    session['chat_history'] = []
    session.modified = True
    return jsonify({'success': True})


@ai_bp.route('/chat/history/add', methods=['POST'])
@login_required
@premium_required
def add_chat_history():
    user_message = request.form.get('user')
    bot_message = request.form.get('bot')
    
    if user_message and bot_message:
        history = session.get('chat_history', [])
        history.append({'user': user_message, 'bot': bot_message})
        session['chat_history'] = history[-10:]
        session.modified = True
        return jsonify({'success': True})
    return jsonify({'error': 'Invalid parameters'}), 400
