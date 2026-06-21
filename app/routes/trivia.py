from flask import Blueprint, render_template, jsonify, request, session
from flask_login import login_required
from app.models.food import FoodItem
from app.extensions import db
import random

trivia_bp = Blueprint('trivia', __name__)

def get_surprising_pair():
    """
    Selects two random food items whose calorie densities differ by less than 40%.
    Includes a fallback in case no matching pair is found within limit.
    """
    foods = FoodItem.query.all()
    if len(foods) < 2:
        return None, None
        
    for _ in range(50):  # Try 50 times to find a close pair
        item1 = random.choice(foods)
        item2 = random.choice(foods)
        
        if item1.id == item2.id:
            continue
            
        c1 = item1.calories_per_100g
        c2 = item2.calories_per_100g
        
        if c1 == 0 or c2 == 0:
            continue
            
        diff_ratio = abs(c1 - c2) / max(c1, c2)
        if diff_ratio < 0.40 and c1 != c2:
            return item1, item2
            
    # Fallback to any two random distinct items
    item1 = random.choice(foods)
    item2 = random.choice(foods)
    while item2.id == item1.id:
        item2 = random.choice(foods)
    return item1, item2


@trivia_bp.route('/', methods=['GET'])
@login_required
def index():
    # Initialize streaks in session if not present
    if 'trivia_streak' not in session:
        session['trivia_streak'] = 0
    if 'trivia_best_streak' not in session:
        session['trivia_best_streak'] = 0

    item1, item2 = get_surprising_pair()
    
    if not item1 or not item2:
        return render_template('trivia/index.html', error="Not enough food items in the database to play trivia. Please seed first.")

    # Store current question pairing in session to prevent cheating/falsifying ID submissions
    session['trivia_item_1_id'] = item1.id
    session['trivia_item_2_id'] = item2.id

    return render_template(
        'trivia/index.html',
        item1=item1,
        item2=item2,
        streak=session['trivia_streak'],
        best_streak=session['trivia_best_streak']
    )


@trivia_bp.route('/next', methods=['GET'])
@login_required
def next_question():
    item1, item2 = get_surprising_pair()
    if not item1 or not item2:
        return jsonify({'error': 'Not enough foods'}), 400
        
    session['trivia_item_1_id'] = item1.id
    session['trivia_item_2_id'] = item2.id
    
    return jsonify({
        'item1': {
            'id': item1.id,
            'name': item1.name,
            'name_hindi': item1.name_hindi or '',
            'category': item1.category
        },
        'item2': {
            'id': item2.id,
            'name': item2.name,
            'name_hindi': item2.name_hindi or '',
            'category': item2.category
        }
    })


@trivia_bp.route('/answer', methods=['POST'])
@login_required
def check_answer():
    data = request.get_json() or {}
    selected_id = data.get('selected_id')
    
    if not selected_id:
        return jsonify({'error': 'No selection made'}), 400
        
    # Get active pairing IDs from session
    id1 = session.get('trivia_item_1_id')
    id2 = session.get('trivia_item_2_id')
    
    if not id1 or not id2 or int(selected_id) not in (id1, id2):
        return jsonify({'error': 'Invalid trivia state'}), 400

    item1 = FoodItem.query.get(id1)
    item2 = FoodItem.query.get(id2)
    
    if not item1 or not item2:
        return jsonify({'error': 'Foods not found'}), 400

    selected_id = int(selected_id)
    c1 = item1.calories_per_100g
    c2 = item2.calories_per_100g
    
    # Correct choice is the one with FEWER calories
    if c1 < c2:
        correct_id = item1.id
        fewer_item = item1
        more_item = item2
    else:
        correct_id = item2.id
        fewer_item = item2
        more_item = item1

    is_correct = selected_id == correct_id
    
    # Update streaks
    if is_correct:
        session['trivia_streak'] += 1
        if session['trivia_streak'] > session['trivia_best_streak']:
            session['trivia_best_streak'] = session['trivia_streak']
    else:
        session['trivia_streak'] = 0
        
    session.modified = True

    # Generate fun fact
    diff = int(abs(item1.calories_per_100g - item2.calories_per_100g))
    fun_facts = [
        f"{fewer_item.name} has only {int(fewer_item.calories_per_100g)} kcal per 100g, while {more_item.name} has {int(more_item.calories_per_100g)} kcal—a difference of {diff} kcal!",
        f"Opting for {fewer_item.name} saves you {diff} kcal per 100g compared to {more_item.name}! Perfect for calorie deficits.",
        f"Did you know? {fewer_item.name} ({int(fewer_item.calories_per_100g)} kcal/100g) is calorie-lighter than {more_item.name} ({int(more_item.calories_per_100g)} kcal/100g)."
    ]
    fun_fact = random.choice(fun_facts)

    return jsonify({
        'correct': is_correct,
        'correct_id': correct_id,
        'calories_item1': c1,
        'calories_item2': c2,
        'streak': session['trivia_streak'],
        'best_streak': session['trivia_best_streak'],
        'fun_fact': fun_fact
    })
