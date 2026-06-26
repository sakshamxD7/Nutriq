# Nutriq — AI-Powered Calorie & Nutrition Tracker

> **Live Demo → [nutriq.onrender.com](https://nutriq.onrender.com/)**

A full-stack nutrition tracking web app built for Indian users. Covers calorie logging, barcode scanning, 30-day food diary, AI diet plan generation, and a streaming AI nutrition chatbot — with a complete free/premium billing tier.

---

## Screenshots

| Dashboard | Food Diary | AI Chatbot |
|:---:|:---:|:---:|
| *(screenshot)* | *(screenshot)* | *(screenshot)* |

---

## Features

**Onboarding & Calorie Targeting**  
New users input age, gender, height, weight, activity level, goal (lose / maintain / gain), and dietary preference (veg / non-veg / vegan / jain). BMR is calculated via the Mifflin-St Jeor equation, converted to TDEE using an activity multiplier, and adjusted ±500 kcal for goal. Minimum floor: 1200 kcal/day.

**Food Logging**  
Log meals across breakfast, lunch, dinner, and snacks. Search from a seeded Indian food database (`seed_foods.py`). Logs store quantity in grams; macros (calories, protein, carbs, fat) calculated at read time.

**Barcode Scanner**  
Camera-based barcode scan via `pyzbar`. Hits the Open Food Facts API, parses nutrient data per 100g (with kJ → kcal fallback), and caches the result in the local `FoodItem` table for future lookups.

**30-Day Food Diary**  
Calendar view of the past 30 days with daily calorie totals, macro breakdown, and per-meal log details. Color-coded against the user's daily target. Includes **CSV export** of the full log history.

**AI Diet Plan (Premium)**  
Calls Gemini 1.5 Flash with a structured JSON schema prompt. Generates a 7-day personalized Indian meal plan tailored to the user's TDEE, dietary preference, cuisine choice, and allergies. Meals from the plan can be logged directly to the diary in one click. Falls back to realistic mock plans (North Indian / South Indian / Mixed) when offline or rate-limited.

**AI Nutrition Chatbot (Premium)**  
Streaming SSE-based chat powered by Gemini 1.5 Flash. Context-aware: knows the user's remaining calories for the day from live food logs. Maintains last 5 exchanges in session history. Falls back to a simulated typewriter stream when no API key is present.

**Nutrition Trivia**  
Gamified trivia module for nutrition knowledge.

**Email Reminders**  
APScheduler + Flask-Mail sends daily meal reminders at user-configured times. Toggle on/off from settings.

**Premium Billing**  
Stripe-integrated checkout for Plus and Pro plans. Includes a simulation mode — if Stripe keys are absent, users are upgraded directly, so the full premium flow is testable without a live Stripe account.

---

## System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                         CLIENT (Browser)                         │
│          Jinja2 Templates + Vanilla JS + Chart.js                │
│          barcode.js (camera scan) · chat.js (SSE stream)         │
└──────────┬───────────────────────────────────────┬───────────────┘
           │ HTTP / SSE                             │
           ▼                                        ▼
┌──────────────────────────────────────────────────────────────────┐
│                    FLASK APPLICATION (run.py)                     │
│                                                                  │
│  Blueprints                                                      │
│  ├── auth        → register, login, logout (Flask-Login)         │
│  ├── dashboard   → KPI summary, macro ring charts                │
│  ├── food        → search, log, barcode scan                     │
│  ├── diary       → 30-day calendar, CSV export                   │
│  ├── goals       → weight logs, target tracking                  │
│  ├── ai          → diet plan (POST) + chatbot (SSE stream)       │
│  ├── billing     → Stripe checkout + simulation mode             │
│  ├── trivia      → nutrition Q&A game                            │
│  └── notifications → reminder settings                           │
│                                                                  │
│  Services                                                        │
│  ├── gemini.py    → Gemini 1.5 Flash (plan gen + chat stream)   │
│  ├── barcode.py   → Open Food Facts API + DB cache              │
│  ├── food_db.py   → Indian food database queries                 │
│  └── scheduler.py → APScheduler daily email reminders           │
└──────────┬──────────────────────────────┬────────────────────────┘
           │ SQLAlchemy ORM               │ External APIs
           ▼                              ▼
┌──────────────────┐         ┌────────────────────────────────────┐
│   SQLite DB      │         │  Gemini 1.5 Flash (Google AI)      │
│                  │         │  Open Food Facts API (barcodes)    │
│  users           │         │  Stripe API (billing)              │
│  food_items      │         │  SMTP / Flask-Mail (reminders)     │
│  food_logs       │         └────────────────────────────────────┘
│  diet_plans      │
│  subscriptions   │
│  weight_logs     │
└──────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12, Flask 3.x |
| Auth | Flask-Login, Flask-Bcrypt, Flask-WTF (CSRF) |
| Database | SQLite, Flask-SQLAlchemy, Flask-Migrate |
| AI | Google Gemini 1.5 Flash (`google-generativeai`) |
| Barcode | pyzbar, Open Food Facts API |
| Billing | Stripe (`stripe` SDK) |
| Scheduler | APScheduler, Flask-Mail |
| Frontend | Jinja2, Vanilla JS, Chart.js |

---

## Project Structure

```
nutriq/
├── run.py                        # App entry point
├── config.py                     # Config classes (dev/prod)
├── requirements.txt
├── seed_foods.py                 # Seeds Indian food database
├── .env.example
│
├── app/
│   ├── __init__.py               # App factory
│   ├── extensions.py             # db, login_manager, mail, csrf
│   │
│   ├── models/
│   │   ├── user.py               # User, BMR/TDEE/calorie target logic
│   │   ├── food.py               # FoodItem, FoodLog
│   │   └── plan.py               # DietPlan, Subscription, WeightLog
│   │
│   ├── routes/
│   │   ├── auth.py               # Register, login, premium_required decorator
│   │   ├── dashboard.py          # Daily KPIs and macro charts
│   │   ├── food.py               # Search, log, barcode
│   │   ├── diary.py              # 30-day view, CSV export
│   │   ├── ai.py                 # Diet plan + streaming chatbot
│   │   ├── billing.py            # Stripe checkout + simulation
│   │   ├── goals.py              # Weight tracking
│   │   ├── trivia.py             # Nutrition trivia
│   │   └── notifications.py     # Reminder settings
│   │
│   ├── services/
│   │   ├── gemini.py             # Gemini API + mock fallbacks
│   │   ├── barcode.py            # Open Food Facts + DB cache
│   │   ├── food_db.py            # Indian food search logic
│   │   └── scheduler.py         # APScheduler email jobs
│   │
│   ├── templates/                # Jinja2 HTML templates
│   └── static/
│       ├── css/main.css
│       └── js/
│           ├── barcode.js        # Camera scan + preview
│           ├── chat.js           # SSE stream handler
│           └── trivia.js
```

---

## Run Locally

```bash
git clone https://github.com/YOUR_USERNAME/nutriq.git
cd nutriq
pip install -r requirements.txt
```

Create a `.env` from the example:
```
GEMINI_API_KEY=your_gemini_key
STRIPE_SECRET_KEY=your_stripe_key
STRIPE_PUBLISHABLE_KEY=your_stripe_pub_key
SECRET_KEY=any_random_string
MAIL_USERNAME=your_email
MAIL_PASSWORD=your_email_password
```

> All external keys are optional. The app runs in **Demo Mode** without them — Gemini falls back to mock meal plans and Stripe upgrades users directly without payment.

```bash
python run.py
# → http://localhost:5000
```

---

## Author

**Saksham Jangir**  
B.Tech CSE (Data Analytics) — JECRC University, Jaipur  
[LinkedIn](https://linkedin.com/in/YOUR_PROFILE) · [GitHub](https://github.com/YOUR_USERNAME)
