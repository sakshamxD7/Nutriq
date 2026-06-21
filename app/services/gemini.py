import os
import json
import logging
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

logger = logging.getLogger(__name__)

# Configure API Key
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def generate_diet_plan(user, preferences):
    """
    Calls the Gemini API to generate a structured 7-day diet plan as a JSON object.
    If no API key is set or on rate limits, falls back to a realistic mock Indian plan.
    """
    duration = preferences.get("duration", 7)
    cuisine = preferences.get("cuisine", "Mixed")
    allergies = preferences.get("allergies", "None")

    system_instruction = (
        "You are an expert Indian nutritionist. Provide a structured weekly diet plan in JSON format. "
        "The output MUST strictly match this JSON schema: "
        '{"days": [{"day": 1, "breakfast": {"name": "string", "quantity": "string", "calories": 0, "protein": 0, "carbs": 0, "fat": 0}, '
        '"lunch": {"name": "string", "quantity": "string", "calories": 0, "protein": 0, "carbs": 0, "fat": 0}, '
        '"dinner": {"name": "string", "quantity": "string", "calories": 0, "protein": 0, "carbs": 0, "fat": 0}, '
        '"snacks": {"name": "string", "quantity": "string", "calories": 0, "protein": 0, "carbs": 0, "fat": 0}, '
        '"total_calories": 0}]}. '
        "Do not include any other text, markdown formatting blocks (like ```json), or explanations outside of the valid JSON object."
    )

    prompt = (
        f"Generate a {duration}-day diet plan for user '{user.name}'. "
        f"User details: Gender: {user.gender}, Age: {user.age}, Weight: {user.weight_kg}kg, Height: {user.height_cm}cm, "
        f"Dietary preference: {user.dietary_pref}, Daily Calorie Target: {user.daily_calorie_target()} kcal. "
        f"Form inputs: Cuisine Preference: {cuisine}, Allergies/Restrictions: {allergies}. "
        f"Please tailor the meals to use common Indian dishes. Ensure total calories for each day matches approximately the target of {user.daily_calorie_target()} kcal."
    )

    if not api_key:
        logger.warning("GEMINI_API_KEY not found. Generating mock diet plan.")
        return get_mock_diet_plan(user, duration, cuisine)

    try:
        model = genai.GenerativeModel(
            model_name="gemini-3-flash-preview",
            generation_config={"response_mime_type": "application/json"}
        )
        response = model.generate_content([system_instruction, prompt])
        plan_json = json.loads(response.text.strip())
        return plan_json
    except ResourceExhausted:
        logger.error("Gemini API rate limit reached.")
        return get_mock_diet_plan(user, duration, cuisine, rate_limited=True)
    except Exception as e:
        logger.error(f"Gemini API error: {str(e)}")
        return get_mock_diet_plan(user, duration, cuisine)


def chat_response(user, today_log, history, user_message):
    """
    Streams a chat response back to the user.
    If no API key is set, yields a simulated streaming response.
    """
    calories_so_far = sum(log.calories for log in today_log)
    remaining_calories = max(0, user.daily_calorie_target() - calories_so_far)
    
    system_instruction = (
        f"You are Nutriq's friendly, expert nutrition assistant. You specialize in Indian foods. "
        f"The user's name is {user.name}. They are a {user.gender}, age {user.age}, height {user.height_cm}cm, weight {user.weight_kg}kg. "
        f"Their dietary preference is {user.dietary_pref}. "
        f"Today, they have logged {int(calories_so_far)} kcal out of their target {user.daily_calorie_target()} kcal. "
        f"Remaining calories for today: {int(remaining_calories)} kcal. "
        "Keep responses short, practical, friendly, and food-centric. Always align recommendations with their daily remaining calories. "
        "If they are close to or over target, suggest light, fiber-rich options like buttermilk, cucumber salad, or clear dal soup."
    )

    # Format previous history for Gemini
    formatted_contents = []
    # Add system context in a message
    formatted_contents.append({"role": "user", "parts": [system_instruction]})
    formatted_contents.append({"role": "model", "parts": ["Understood. I will act as Nutriq's Indian nutrition assistant with those parameters."] })
    
    for exchange in history:
        formatted_contents.append({"role": "user", "parts": [exchange['user']]})
        formatted_contents.append({"role": "model", "parts": [exchange['bot']]})
        
    formatted_contents.append({"role": "user", "parts": [user_message]})

    if not api_key:
        yield from get_mock_chat_stream(user_message, remaining_calories)
        return

    try:
        model = genai.GenerativeModel(model_name="gemini-2.5-flash")
        response = model.generate_content(formatted_contents, stream=True)
        for chunk in response:
            if chunk.text:
                yield chunk.text
    except ResourceExhausted:
        yield "Our AI is taking a quick break (Rate Limit Reached). Try again in a minute."
    except Exception as e:
        logger.error(f"Gemini streaming chat error: {str(e)}")
        yield "I'm having trouble connecting to my brain right now. "
        yield from get_mock_chat_stream(user_message, remaining_calories)


# --- FALLBACK MOCK DATA GENERATORS ---

def get_mock_diet_plan(user, duration, cuisine, rate_limited=False):
    """Generates a structured, valid JSON diet plan locally as a fallback."""
    days = []
    target = user.daily_calorie_target()
    
    # Custom meal lists based on cuisine
    if "south" in cuisine.lower():
        breakfast = {"name": "Idli (3 pcs) with Sambar & Coconut Chutney", "quantity": "1 plate", "calories": int(target * 0.25), "protein": 9, "carbs": 48, "fat": 6}
        lunch = {"name": "Brown Rice with Rasam, Beans Poriyal & Curd", "quantity": "1 plate", "calories": int(target * 0.35), "protein": 12, "carbs": 65, "fat": 8}
        dinner = {"name": "Ragi Dosa (2 pcs) with Tomato Chutney & Boiled Chana", "quantity": "1 plate", "calories": int(target * 0.30), "protein": 14, "carbs": 55, "fat": 9}
        snacks = {"name": "Filter Coffee (with low fat milk) & Roasted Makhana", "quantity": "1 cup + 1 bowl", "calories": int(target * 0.10), "protein": 4, "carbs": 20, "fat": 3}
    elif "north" in cuisine.lower():
        breakfast = {"name": "Aloo Paratha (1 pc) with Curd & Mint Chutney", "quantity": "1 plate", "calories": int(target * 0.25), "protein": 8, "carbs": 45, "fat": 10}
        lunch = {"name": "Roti (2 pcs) with Dal Tadka & Bhindi Masala", "quantity": "1 plate", "calories": int(target * 0.35), "protein": 15, "carbs": 60, "fat": 11}
        dinner = {"name": "Paneer Bhurji / Chicken Curry with 1 Roti & Cucumber Salad", "quantity": "1 plate", "calories": int(target * 0.30), "protein": 24, "carbs": 35, "fat": 14}
        snacks = {"name": "Masala Chai & Roasted Gram (Chana)", "quantity": "1 cup + 1 handful", "calories": int(target * 0.10), "protein": 6, "carbs": 18, "fat": 3}
    else:
        breakfast = {"name": "Vegetable Upma / Poha with Peanuts", "quantity": "1 bowl", "calories": int(target * 0.25), "protein": 7, "carbs": 42, "fat": 7}
        lunch = {"name": "Jeera Rice with Dal Makhani & Mixed Veg Sabzi", "quantity": "1 plate", "calories": int(target * 0.35), "protein": 13, "carbs": 62, "fat": 10}
        dinner = {"name": "Wheat Roti (2 pcs) with Moong Dal & Palak Paneer", "quantity": "1 plate", "calories": int(target * 0.30), "protein": 18, "carbs": 48, "fat": 12}
        snacks = {"name": "Buttermilk (Chaas) & Sprouted Moong Salad", "quantity": "1 glass + 1 bowl", "calories": int(target * 0.10), "protein": 8, "carbs": 15, "fat": 1}

    for d in range(1, duration + 1):
        days.append({
            "day": d,
            "breakfast": breakfast,
            "lunch": lunch,
            "dinner": dinner,
            "snacks": snacks,
            "total_calories": breakfast["calories"] + lunch["calories"] + dinner["calories"] + snacks["calories"]
        })
        
    warning_note = " (Note: Running in Demo Offline Mode)" if not rate_limited else " (Note: Rate Limited - Showing Cached Plan)"
    for d in days:
        d["breakfast"]["name"] += warning_note
        
    return {"days": days}


def get_mock_chat_stream(user_message, remaining_calories):
    """Simulates a typewriter text stream for chatbot fallback."""
    msg = user_message.lower()
    
    intro = "[Demo Mode] "
    if "hello" in msg or "hi" in msg:
        words = f"{intro}Hello there! How can I assist you with your diet and calorie goals today? I can analyze your meals or suggest low-calorie options."
    elif "weight" in msg or "lose" in msg:
        words = f"{intro}To support weight management, aim for a consistent daily caloric deficit. You have {int(remaining_calories)} calories left today. Focusing on lean protein (like paneer, egg whites, dal) and lots of greens will keep you full."
    elif "calorie" in msg or "eat" in msg or "dinner" in msg or "lunch" in msg:
        words = f"{intro}With {int(remaining_calories)} calories remaining, I recommend a balanced meal. Consider 2 multi-grain Rotis with a bowl of Yellow Dal and Cucumber Salad. This offers solid protein and complex carbs without overloading fat."
    else:
        words = f"{intro}That's an interesting question! For general health, ensure you hit your daily protein goal while keeping carbohydrates complex. Since you have {int(remaining_calories)} calories remaining, try choosing nutrient-dense whole foods."

    # Split into chunks of 3-4 letters or words to simulate SSE
    chunk_size = 8
    for i in range(0, len(words), chunk_size):
        yield words[i:i+chunk_size]
