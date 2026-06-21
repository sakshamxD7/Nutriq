from app import create_app
from app.extensions import db
from app.models.food import FoodItem

foods = [
    # --- BREAKFAST ---
    {"name": "Idli", "name_hindi": "इडली", "category": "Breakfast", "calories_per_100g": 112, "protein_g": 3.2, "carbs_g": 23.0, "fat_g": 0.5, "fiber_g": 1.2, "region": "South India"},
    {"name": "Dosa (Plain)", "name_hindi": "डोसा (सादा)", "category": "Breakfast", "calories_per_100g": 168, "protein_g": 3.9, "carbs_g": 29.0, "fat_g": 3.7, "fiber_g": 1.4, "region": "South India"},
    {"name": "Masala Dosa", "name_hindi": "मसाला डोसा", "category": "Breakfast", "calories_per_100g": 175, "protein_g": 4.1, "carbs_g": 30.5, "fat_g": 4.0, "fiber_g": 1.8, "region": "South India"},
    {"name": "Upma", "name_hindi": "उपमा", "category": "Breakfast", "calories_per_100g": 132, "protein_g": 2.8, "carbs_g": 21.0, "fat_g": 4.1, "fiber_g": 1.6, "region": "South India"},
    {"name": "Poha", "name_hindi": "पोहा", "category": "Breakfast", "calories_per_100g": 180, "protein_g": 3.5, "carbs_g": 32.0, "fat_g": 4.2, "fiber_g": 1.9, "region": "Maharashtra/MP"},
    {"name": "Aloo Paratha", "name_hindi": "आलू पराठा", "category": "Breakfast", "calories_per_100g": 210, "protein_g": 5.0, "carbs_g": 33.0, "fat_g": 6.8, "fiber_g": 2.5, "region": "Punjab"},
    {"name": "Paneer Paratha", "name_hindi": "पनीर पराठा", "category": "Breakfast", "calories_per_100g": 240, "protein_g": 9.2, "carbs_g": 31.0, "fat_g": 8.5, "fiber_g": 2.2, "region": "Punjab"},
    {"name": "Plain Paratha", "name_hindi": "सादा पराठा", "category": "Breakfast", "calories_per_100g": 258, "protein_g": 5.2, "carbs_g": 38.0, "fat_g": 9.0, "fiber_g": 2.4, "region": "North India"},
    {"name": "Puri", "name_hindi": "पूरी", "category": "Breakfast", "calories_per_100g": 320, "protein_g": 6.0, "carbs_g": 46.0, "fat_g": 12.0, "fiber_g": 2.1, "region": "North India"},
    {"name": "Chole Bhature", "name_hindi": "छोले भटूरे", "category": "Breakfast", "calories_per_100g": 280, "protein_g": 7.5, "carbs_g": 38.0, "fat_g": 11.2, "fiber_g": 4.5, "region": "Delhi/Punjab"},
    {"name": "Medu Vada", "name_hindi": "मेदु वड़ा", "category": "Breakfast", "calories_per_100g": 195, "protein_g": 5.5, "carbs_g": 22.0, "fat_g": 9.5, "fiber_g": 2.8, "region": "South India"},
    {"name": "Uttapam", "name_hindi": "उत्तपम", "category": "Breakfast", "calories_per_100g": 150, "protein_g": 3.5, "carbs_g": 26.0, "fat_g": 3.2, "fiber_g": 1.7, "region": "South India"},
    {"name": "Besan Cheela", "name_hindi": "बेसन चीला", "category": "Breakfast", "calories_per_100g": 160, "protein_g": 7.8, "carbs_g": 22.0, "fat_g": 4.5, "fiber_g": 3.0, "region": "North India"},
    {"name": "Sabudana Khichdi", "name_hindi": "साबूदाना खिचड़ी", "category": "Breakfast", "calories_per_100g": 189, "protein_g": 1.5, "carbs_g": 35.0, "fat_g": 4.8, "fiber_g": 0.9, "region": "Maharashtra"},
    {"name": "Appam", "name_hindi": "अप्पम", "category": "Breakfast", "calories_per_100g": 120, "protein_g": 2.1, "carbs_g": 24.0, "fat_g": 1.5, "fiber_g": 0.8, "region": "Kerala"},

    # --- LUNCH/DINNER STAPLES ---
    {"name": "Dal Tadka", "name_hindi": "दाल तड़का", "category": "Lunch/Dinner staples", "calories_per_100g": 118, "protein_g": 6.2, "carbs_g": 15.0, "fat_g": 3.8, "fiber_g": 4.0, "region": "North India"},
    {"name": "Dal Makhani", "name_hindi": "दाल मखनी", "category": "Lunch/Dinner staples", "calories_per_100g": 152, "protein_g": 5.8, "carbs_g": 16.2, "fat_g": 7.2, "fiber_g": 4.2, "region": "Punjab"},
    {"name": "Rajma Masala", "name_hindi": "राजमा मसाला", "category": "Lunch/Dinner staples", "calories_per_100g": 124, "protein_g": 6.8, "carbs_g": 17.5, "fat_g": 3.2, "fiber_g": 4.8, "region": "Punjab"},
    {"name": "Chole Masala", "name_hindi": "छोले मसाला", "category": "Lunch/Dinner staples", "calories_per_100g": 140, "protein_g": 7.0, "carbs_g": 19.0, "fat_g": 4.0, "fiber_g": 5.1, "region": "North India"},
    {"name": "Palak Paneer", "name_hindi": "पालक पनीर", "category": "Lunch/Dinner staples", "calories_per_100g": 116, "protein_g": 6.5, "carbs_g": 4.2, "fat_g": 8.4, "fiber_g": 2.0, "region": "Punjab"},
    {"name": "Paneer Butter Masala", "name_hindi": "पनीर बटर मसाला", "category": "Lunch/Dinner staples", "calories_per_100g": 229, "protein_g": 8.0, "carbs_g": 7.8, "fat_g": 18.5, "fiber_g": 1.1, "region": "Punjab"},
    {"name": "Aloo Gobi", "name_hindi": "आलू गोभी", "category": "Lunch/Dinner staples", "calories_per_100g": 95, "protein_g": 2.0, "carbs_g": 12.0, "fat_g": 4.5, "fiber_g": 2.6, "region": "North India"},
    {"name": "Bhindi Masala", "name_hindi": "भिंडी मसाला", "category": "Lunch/Dinner staples", "calories_per_100g": 88, "protein_g": 2.1, "carbs_g": 10.0, "fat_g": 4.8, "fiber_g": 3.2, "region": "North India"},
    {"name": "Baingan Bharta", "name_hindi": "बैंगन भर्ता", "category": "Lunch/Dinner staples", "calories_per_100g": 78, "protein_g": 1.8, "carbs_g": 8.5, "fat_g": 4.2, "fiber_g": 3.0, "region": "North India"},
    {"name": "Kadhi Pakora", "name_hindi": "कढ़ी पकोड़ा", "category": "Lunch/Dinner staples", "calories_per_100g": 122, "protein_g": 4.2, "carbs_g": 13.0, "fat_g": 6.0, "fiber_g": 1.5, "region": "North/West India"},
    {"name": "Sambar", "name_hindi": "सांभर", "category": "Lunch/Dinner staples", "calories_per_100g": 62, "protein_g": 2.5, "carbs_g": 9.5, "fat_g": 1.6, "fiber_g": 2.2, "region": "South India"},
    {"name": "Rasam", "name_hindi": "रसम", "category": "Lunch/Dinner staples", "calories_per_100g": 45, "protein_g": 1.1, "carbs_g": 6.8, "fat_g": 1.4, "fiber_g": 1.0, "region": "South India"},
    {"name": "Mix Vegetable", "name_hindi": "मिक्स वेज", "category": "Lunch/Dinner staples", "calories_per_100g": 92, "protein_g": 2.2, "carbs_g": 11.5, "fat_g": 4.2, "fiber_g": 2.8, "region": "North India"},
    {"name": "Aloo Matar", "name_hindi": "आलू मटर", "category": "Lunch/Dinner staples", "calories_per_100g": 110, "protein_g": 2.5, "carbs_g": 16.0, "fat_g": 4.0, "fiber_g": 3.0, "region": "North India"},
    {"name": "Lauki Ki Sabzi", "name_hindi": "लौकी की सब्जी", "category": "Lunch/Dinner staples", "calories_per_100g": 48, "protein_g": 1.0, "carbs_g": 4.5, "fat_g": 2.8, "fiber_g": 1.5, "region": "North India"},
    {"name": "Dum Aloo", "name_hindi": "दम आलू", "category": "Lunch/Dinner staples", "calories_per_100g": 145, "protein_g": 2.8, "carbs_g": 18.2, "fat_g": 6.8, "fiber_g": 2.2, "region": "Kashmir/Bengal"},
    {"name": "Matar Paneer", "name_hindi": "मटर पनीर", "category": "Lunch/Dinner staples", "calories_per_100g": 165, "protein_g": 7.5, "carbs_g": 11.0, "fat_g": 10.2, "fiber_g": 2.4, "region": "North India"},
    {"name": "Malai Kofta", "name_hindi": "मलाई कोफ्ता", "category": "Lunch/Dinner staples", "calories_per_100g": 268, "protein_g": 6.0, "carbs_g": 20.0, "fat_g": 18.0, "fiber_g": 1.9, "region": "Punjab"},
    {"name": "Avial", "name_hindi": "अवियल", "category": "Lunch/Dinner staples", "calories_per_100g": 128, "protein_g": 2.4, "carbs_g": 9.8, "fat_g": 8.9, "fiber_g": 3.1, "region": "Kerala"},
    {"name": "Toran (Cabbage)", "name_hindi": "थोरन (पत्तागोभी)", "category": "Lunch/Dinner staples", "calories_per_100g": 72, "protein_g": 1.9, "carbs_g": 7.0, "fat_g": 4.1, "fiber_g": 2.6, "region": "Kerala"},

    # --- RICE DISHES ---
    {"name": "Plain rice (boiled)", "name_hindi": "उबला हुआ चावल", "category": "Rice dishes", "calories_per_100g": 130, "protein_g": 2.7, "carbs_g": 28.0, "fat_g": 0.3, "fiber_g": 0.4, "region": "Pan-India"},
    {"name": "Jeera rice", "name_hindi": "जीरा राइस", "category": "Rice dishes", "calories_per_100g": 140, "protein_g": 2.8, "carbs_g": 29.5, "fat_g": 1.2, "fiber_g": 0.5, "region": "North India"},
    {"name": "Vegetable Biryani", "name_hindi": "वेज बिरयानी", "category": "Rice dishes", "calories_per_100g": 165, "protein_g": 4.0, "carbs_g": 28.0, "fat_g": 4.2, "fiber_g": 1.8, "region": "Hyderabad/Lucknow"},
    {"name": "Chicken Biryani", "name_hindi": "चिकन बिरयानी", "category": "Rice dishes", "calories_per_100g": 190, "protein_g": 9.5, "carbs_g": 26.0, "fat_g": 5.5, "fiber_g": 1.4, "region": "Hyderabad"},
    {"name": "Vegetable Pulao", "name_hindi": "वेज पुलाव", "category": "Rice dishes", "calories_per_100g": 138, "protein_g": 3.0, "carbs_g": 26.5, "fat_g": 2.2, "fiber_g": 1.5, "region": "North India"},
    {"name": "Khichdi (Moong Dal)", "name_hindi": "खिचड़ी (मूंग दाल)", "category": "Rice dishes", "calories_per_100g": 110, "protein_g": 4.2, "carbs_g": 21.0, "fat_g": 1.0, "fiber_g": 1.8, "region": "Pan-India"},
    {"name": "Curd rice", "name_hindi": "दही चावल", "category": "Rice dishes", "calories_per_100g": 128, "protein_g": 3.8, "carbs_g": 21.0, "fat_g": 3.0, "fiber_g": 0.9, "region": "South India"},
    {"name": "Lemon rice", "name_hindi": "लेमन राइस", "category": "Rice dishes", "calories_per_100g": 154, "protein_g": 3.2, "carbs_g": 28.5, "fat_g": 3.0, "fiber_g": 1.1, "region": "South India"},
    {"name": "Brown Rice (cooked)", "name_hindi": "पका हुआ भूरा चावल", "category": "Rice dishes", "calories_per_100g": 111, "protein_g": 2.6, "carbs_g": 23.0, "fat_g": 0.9, "fiber_g": 1.8, "region": "Global"},
    {"name": "Tomato Bath", "name_hindi": "टमाटर बाथ", "category": "Rice dishes", "calories_per_100g": 142, "protein_g": 3.1, "carbs_g": 26.8, "fat_g": 2.5, "fiber_g": 1.4, "region": "South India"},
    {"name": "Tamarind Rice (Puliyogare)", "name_hindi": "इमली चावल", "category": "Rice dishes", "calories_per_100g": 182, "protein_g": 3.8, "carbs_g": 31.0, "fat_g": 4.8, "fiber_g": 1.6, "region": "South India"},

    # --- BREADS ---
    {"name": "Roti (home)", "name_hindi": "घर की रोटी", "category": "Breads", "calories_per_100g": 264, "protein_g": 9.0, "carbs_g": 54.0, "fat_g": 1.2, "fiber_g": 8.0, "region": "Pan-India"},
    {"name": "Roti (restaurant/tandoori)", "name_hindi": "तंदूरी रोटी", "category": "Breads", "calories_per_100g": 272, "protein_g": 9.5, "carbs_g": 56.0, "fat_g": 1.0, "fiber_g": 7.5, "region": "North India"},
    {"name": "Butter Naan", "name_hindi": "बटर नान", "category": "Breads", "calories_per_100g": 312, "protein_g": 8.8, "carbs_g": 50.0, "fat_g": 8.5, "fiber_g": 2.1, "region": "North India"},
    {"name": "Garlic Naan", "name_hindi": "लहसुन नान", "category": "Breads", "calories_per_100g": 320, "protein_g": 9.0, "carbs_g": 51.0, "fat_g": 8.8, "fiber_g": 2.2, "region": "North India"},
    {"name": "Plain Naan", "name_hindi": "सादा नान", "category": "Breads", "calories_per_100g": 290, "protein_g": 8.5, "carbs_g": 52.0, "fat_g": 5.0, "fiber_g": 2.0, "region": "North India"},
    {"name": "Kulcha", "name_hindi": "कुलचा", "category": "Breads", "calories_per_100g": 285, "protein_g": 7.8, "carbs_g": 54.0, "fat_g": 4.2, "fiber_g": 1.9, "region": "Punjab"},
    {"name": "Bhakri (Jowar)", "name_hindi": "भाकरी (ज्वार)", "category": "Breads", "calories_per_100g": 240, "protein_g": 8.2, "carbs_g": 49.0, "fat_g": 1.6, "fiber_g": 6.8, "region": "Maharashtra"},
    {"name": "Bhakri (Bajra)", "name_hindi": "भाकरी (बाजरा)", "category": "Breads", "calories_per_100g": 250, "protein_g": 9.0, "carbs_g": 47.0, "fat_g": 2.5, "fiber_g": 7.2, "region": "Rajasthan/Gujarat"},
    {"name": "Missi Roti", "name_hindi": "मिस्सी रोटी", "category": "Breads", "calories_per_100g": 280, "protein_g": 11.2, "carbs_g": 48.0, "fat_g": 4.8, "fiber_g": 5.5, "region": "Rajasthan/Punjab"},
    {"name": "Lachha Paratha", "name_hindi": "लच्छा पराठा", "category": "Breads", "calories_per_100g": 320, "protein_g": 6.5, "carbs_g": 46.0, "fat_g": 12.0, "fiber_g": 2.2, "region": "North India"},
    {"name": "Appam (Laced)", "name_hindi": "अप्पम", "category": "Breads", "calories_per_100g": 140, "protein_g": 2.3, "carbs_g": 27.0, "fat_g": 2.5, "fiber_g": 0.9, "region": "Kerala"},
    {"name": "Rumali Roti", "name_hindi": "रूमाली रोटी", "category": "Breads", "calories_per_100g": 280, "protein_g": 8.0, "carbs_g": 58.0, "fat_g": 1.5, "fiber_g": 3.0, "region": "North India"},

    # --- STREET FOOD ---
    {"name": "Samosa", "name_hindi": "समोसा", "category": "Street food", "calories_per_100g": 262, "protein_g": 4.5, "carbs_g": 32.0, "fat_g": 13.0, "fiber_g": 2.0, "region": "Pan-India"},
    {"name": "Vada Pav", "name_hindi": "वड़ा पाव", "category": "Street food", "calories_per_100g": 242, "protein_g": 6.1, "carbs_g": 38.0, "fat_g": 7.5, "fiber_g": 3.5, "region": "Maharashtra"},
    {"name": "Pani Puri", "name_hindi": "पानी पूरी", "category": "Street food", "calories_per_100g": 110, "protein_g": 2.2, "carbs_g": 21.0, "fat_g": 1.8, "fiber_g": 2.5, "region": "Pan-India"},
    {"name": "Bhel Puri", "name_hindi": "भेल पूरी", "category": "Street food", "calories_per_100g": 145, "protein_g": 3.2, "carbs_g": 26.0, "fat_g": 3.1, "fiber_g": 2.4, "region": "Maharashtra"},
    {"name": "Aloo Tikki", "name_hindi": "आलू टिक्की", "category": "Street food", "calories_per_100g": 178, "protein_g": 2.8, "carbs_g": 24.0, "fat_g": 7.8, "fiber_g": 2.1, "region": "North India"},
    {"name": "Dahi Puri", "name_hindi": "दही पूरी", "category": "Street food", "calories_per_100g": 180, "protein_g": 4.0, "carbs_g": 28.0, "fat_g": 5.5, "fiber_g": 2.0, "region": "Maharashtra"},
    {"name": "Kachori (Pyaaz)", "name_hindi": "कचौड़ी", "category": "Street food", "calories_per_100g": 380, "protein_g": 6.8, "carbs_g": 44.0, "fat_g": 20.0, "fiber_g": 2.8, "region": "Rajasthan"},
    {"name": "Pav Bhaji", "name_hindi": "पाव भाजी", "category": "Street food", "calories_per_100g": 160, "protein_g": 4.5, "carbs_g": 22.0, "fat_g": 6.0, "fiber_g": 2.9, "region": "Maharashtra"},
    {"name": "Chana Chaat", "name_hindi": "चना चाट", "category": "Street food", "calories_per_100g": 135, "protein_g": 6.5, "carbs_g": 21.5, "fat_g": 2.5, "fiber_g": 4.8, "region": "North India"},
    {"name": "Papdi Chaat", "name_hindi": "पापड़ी चाट", "category": "Street food", "calories_per_100g": 210, "protein_g": 4.5, "carbs_g": 32.0, "fat_g": 7.0, "fiber_g": 2.1, "region": "North India"},
    {"name": "Dahi Vada", "name_hindi": "दही वड़ा", "category": "Street food", "calories_per_100g": 154, "protein_g": 5.8, "carbs_g": 18.0, "fat_g": 6.5, "fiber_g": 1.9, "region": "Pan-India"},
    {"name": "Khandvi", "name_hindi": "खांडवी", "category": "Street food", "calories_per_100g": 120, "protein_g": 4.8, "carbs_g": 15.0, "fat_g": 4.5, "fiber_g": 2.2, "region": "Gujarat"},
    {"name": "Dhokla (Khaman)", "name_hindi": "ढोकला", "category": "Street food", "calories_per_100g": 130, "protein_g": 4.5, "carbs_g": 22.0, "fat_g": 2.8, "fiber_g": 1.4, "region": "Gujarat"},
    {"name": "Momo (Veg, steamed)", "name_hindi": "मोमो", "category": "Street food", "calories_per_100g": 112, "protein_g": 3.8, "carbs_g": 22.5, "fat_g": 0.8, "fiber_g": 1.2, "region": "North East"},
    {"name": "Egg Roll (Kolkata)", "name_hindi": "एग रोल", "category": "Street food", "calories_per_100g": 245, "protein_g": 8.5, "carbs_g": 32.0, "fat_g": 9.5, "fiber_g": 1.6, "region": "West Bengal"},

    # --- SNACKS ---
    {"name": "Namkeen mixture", "name_hindi": "नमकीन मिक्सचर", "category": "Snacks", "calories_per_100g": 520, "protein_g": 11.0, "carbs_g": 42.0, "fat_g": 34.0, "fiber_g": 3.2, "region": "Pan-India"},
    {"name": "Chakli", "name_hindi": "चकली", "category": "Snacks", "calories_per_100g": 505, "protein_g": 7.5, "carbs_g": 54.0, "fat_g": 28.5, "fiber_g": 2.8, "region": "Maharashtra/South"},
    {"name": "Murukku", "name_hindi": "मुरुक्कू", "category": "Snacks", "calories_per_100g": 510, "protein_g": 7.8, "carbs_g": 53.0, "fat_g": 29.0, "fiber_g": 2.9, "region": "South India"},
    {"name": "Mathri", "name_hindi": "मठरी", "category": "Snacks", "calories_per_100g": 480, "protein_g": 8.2, "carbs_g": 52.0, "fat_g": 26.0, "fiber_g": 2.4, "region": "North India"},
    {"name": "Khakhra (Plain)", "name_hindi": "खाखरा", "category": "Snacks", "calories_per_100g": 410, "protein_g": 9.5, "carbs_g": 68.0, "fat_g": 11.0, "fiber_g": 5.0, "region": "Gujarat"},
    {"name": "Roasted Makhana", "name_hindi": "भुना मखाना", "category": "Snacks", "calories_per_100g": 360, "protein_g": 9.0, "carbs_g": 74.0, "fat_g": 1.0, "fiber_g": 7.6, "region": "North India"},
    {"name": "Banana Chips", "name_hindi": "केले के चिप्स", "category": "Snacks", "calories_per_100g": 519, "protein_g": 2.3, "carbs_g": 58.4, "fat_g": 30.0, "fiber_g": 4.2, "region": "Kerala"},
    {"name": "Roasted Chana", "name_hindi": "भुना चना", "category": "Snacks", "calories_per_100g": 355, "protein_g": 20.0, "carbs_g": 55.0, "fat_g": 6.0, "fiber_g": 15.0, "region": "Pan-India"},
    {"name": "Peanut Chikki", "name_hindi": "चिक्की", "category": "Snacks", "calories_per_100g": 482, "protein_g": 13.5, "carbs_g": 52.0, "fat_g": 24.5, "fiber_g": 3.8, "region": "West/South India"},
    {"name": "Papad (Roasted)", "name_hindi": "भुना पापड़", "category": "Snacks", "calories_per_100g": 310, "protein_g": 19.0, "carbs_g": 56.0, "fat_g": 1.2, "fiber_g": 11.0, "region": "Pan-India"},
    {"name": "Almonds", "name_hindi": "बादाम", "category": "Snacks", "calories_per_100g": 579, "protein_g": 21.2, "carbs_g": 21.6, "fat_g": 49.9, "fiber_g": 12.5, "region": "Global"},
    {"name": "Cashews", "name_hindi": "काजू", "category": "Snacks", "calories_per_100g": 553, "protein_g": 18.2, "carbs_g": 30.2, "fat_g": 43.8, "fiber_g": 3.3, "region": "Global"},

    # --- SWEETS/DESSERTS ---
    {"name": "Gulab Jamun", "name_hindi": "गुलाब जामुन", "category": "Sweets/Desserts", "calories_per_100g": 380, "protein_g": 4.8, "carbs_g": 58.0, "fat_g": 14.5, "fiber_g": 0.5, "region": "Pan-India"},
    {"name": "Rasgulla", "name_hindi": "रसगुल्ला", "category": "Sweets/Desserts", "calories_per_100g": 186, "protein_g": 4.0, "carbs_g": 38.0, "fat_g": 1.8, "fiber_g": 0.2, "region": "East India/Bengal"},
    {"name": "Kheer", "name_hindi": "खीर", "category": "Sweets/Desserts", "calories_per_100g": 140, "protein_g": 3.8, "carbs_g": 22.0, "fat_g": 4.0, "fiber_g": 0.2, "region": "Pan-India"},
    {"name": "Suji Halwa", "name_hindi": "सूजी हलवा", "category": "Sweets/Desserts", "calories_per_100g": 285, "protein_g": 3.5, "carbs_g": 52.0, "fat_g": 7.2, "fiber_g": 1.0, "region": "North India"},
    {"name": "Moong Dal Halwa", "name_hindi": "मूंग दाल हलवा", "category": "Sweets/Desserts", "calories_per_100g": 395, "protein_g": 7.2, "carbs_g": 51.0, "fat_g": 18.0, "fiber_g": 2.2, "region": "Rajasthan/North"},
    {"name": "Besan Ladoo", "name_hindi": "बेसन लड्डू", "category": "Sweets/Desserts", "calories_per_100g": 472, "protein_g": 8.0, "carbs_g": 58.0, "fat_g": 23.0, "fiber_g": 2.0, "region": "North India"},
    {"name": "Jalebi", "name_hindi": "जलेबी", "category": "Sweets/Desserts", "calories_per_100g": 300, "protein_g": 2.2, "carbs_g": 70.0, "fat_g": 1.5, "fiber_g": 0.4, "region": "Pan-India"},
    {"name": "Kaju Katli", "name_hindi": "काजू कतली", "category": "Sweets/Desserts", "calories_per_100g": 400, "protein_g": 7.8, "carbs_g": 56.0, "fat_g": 16.0, "fiber_g": 0.8, "region": "North India"},
    {"name": "Rasmalai", "name_hindi": "रसमलाई", "category": "Sweets/Desserts", "calories_per_100g": 220, "protein_g": 6.8, "carbs_g": 24.0, "fat_g": 10.8, "fiber_g": 0.3, "region": "West Bengal"},
    {"name": "Gajar Halwa", "name_hindi": "गाजर हलवा", "category": "Sweets/Desserts", "calories_per_100g": 218, "protein_g": 3.2, "carbs_g": 26.0, "fat_g": 11.2, "fiber_g": 1.5, "region": "North India"},
    {"name": "Peda (Mathura)", "name_hindi": "पेड़ा", "category": "Sweets/Desserts", "calories_per_100g": 390, "protein_g": 8.0, "carbs_g": 62.0, "fat_g": 12.0, "fiber_g": 0.1, "region": "Uttar Pradesh"},
    {"name": "Mysore Pak", "name_hindi": "मैसूर पाक", "category": "Sweets/Desserts", "calories_per_100g": 540, "protein_g": 3.8, "carbs_g": 54.0, "fat_g": 34.0, "fiber_g": 0.6, "region": "Karnataka"},

    # --- DRINKS ---
    {"name": "Lassi (sweet)", "name_hindi": "मीठी लस्सी", "category": "Drinks", "calories_per_100g": 88, "protein_g": 2.5, "carbs_g": 13.0, "fat_g": 2.8, "fiber_g": 0.0, "region": "Punjab"},
    {"name": "Lassi (salted)", "name_hindi": "नमकीन लस्सी", "category": "Drinks", "calories_per_100g": 40, "protein_g": 2.6, "carbs_g": 3.5, "fat_g": 1.8, "fiber_g": 0.0, "region": "Punjab"},
    {"name": "Chai (with milk & sugar)", "name_hindi": "चाय", "category": "Drinks", "calories_per_100g": 54, "protein_g": 1.2, "carbs_g": 9.0, "fat_g": 1.5, "fiber_g": 0.0, "region": "Pan-India"},
    {"name": "Filter coffee", "name_hindi": "फ़िल्टर कॉफ़ी", "category": "Drinks", "calories_per_100g": 62, "protein_g": 1.4, "carbs_g": 9.5, "fat_g": 1.8, "fiber_g": 0.0, "region": "South India"},
    {"name": "Nimbu pani (lemonade)", "name_hindi": "नींबू पानी", "category": "Drinks", "calories_per_100g": 32, "protein_g": 0.2, "carbs_g": 8.0, "fat_g": 0.0, "fiber_g": 0.2, "region": "Pan-India"},
    {"name": "Buttermilk (Chaas)", "name_hindi": "छाछ", "category": "Drinks", "calories_per_100g": 28, "protein_g": 1.6, "carbs_g": 2.4, "fat_g": 1.2, "fiber_g": 0.0, "region": "Pan-India"},
    {"name": "Aam Panna", "name_hindi": "आम पन्ना", "category": "Drinks", "calories_per_100g": 68, "protein_g": 0.4, "carbs_g": 16.5, "fat_g": 0.1, "fiber_g": 0.6, "region": "North/West India"},
    {"name": "Coconut Water", "name_hindi": "नारियल पानी", "category": "Drinks", "calories_per_100g": 19, "protein_g": 0.7, "carbs_g": 3.7, "fat_g": 0.2, "fiber_g": 1.1, "region": "Coastal India"},
    {"name": "Sugarcane Juice", "name_hindi": "गन्ने का रस", "category": "Drinks", "calories_per_100g": 78, "protein_g": 0.1, "carbs_g": 20.0, "fat_g": 0.0, "fiber_g": 0.5, "region": "Pan-India"},
    {"name": "Masala Soda", "name_hindi": "मसाला सोडा", "category": "Drinks", "calories_per_100g": 35, "protein_g": 0.1, "carbs_g": 8.5, "fat_g": 0.0, "fiber_g": 0.1, "region": "North India"},

    # --- PROTEINS / MAIN ENTREES ---
    {"name": "Chicken curry", "name_hindi": "चिकन करी", "category": "Proteins", "calories_per_100g": 148, "protein_g": 16.5, "carbs_g": 4.5, "fat_g": 7.2, "fiber_g": 0.8, "region": "Pan-India"},
    {"name": "Egg curry", "name_hindi": "अंडा करी", "category": "Proteins", "calories_per_100g": 135, "protein_g": 9.2, "carbs_g": 4.8, "fat_g": 8.8, "fiber_g": 0.6, "region": "Pan-India"},
    {"name": "Fish curry", "name_hindi": "मछली करी", "category": "Proteins", "calories_per_100g": 128, "protein_g": 15.0, "carbs_g": 3.8, "fat_g": 5.8, "fiber_g": 0.5, "region": "Coastal India"},
    {"name": "Mutton curry", "name_hindi": "मटन करी", "category": "Proteins", "calories_per_100g": 195, "protein_g": 18.0, "carbs_g": 4.0, "fat_g": 11.8, "fiber_g": 0.8, "region": "Pan-India"},
    {"name": "Paneer (raw)", "name_hindi": "पनीर (कच्चा)", "category": "Proteins", "calories_per_100g": 265, "protein_g": 18.3, "carbs_g": 1.2, "fat_g": 20.8, "fiber_g": 0.0, "region": "Pan-India"},
    {"name": "Boiled egg", "name_hindi": "उबला हुआ अंडा", "category": "Proteins", "calories_per_100g": 155, "protein_g": 12.6, "carbs_g": 1.1, "fat_g": 10.6, "fiber_g": 0.0, "region": "Global"},
    {"name": "Grilled chicken (breast)", "name_hindi": "ग्रिल्ड चिकन", "category": "Proteins", "calories_per_100g": 165, "protein_g": 31.0, "carbs_g": 0.0, "fat_g": 3.6, "fiber_g": 0.0, "region": "Global"},
    {"name": "Tandoori Chicken", "name_hindi": "तंदूरी चिकन", "category": "Proteins", "calories_per_100g": 178, "protein_g": 24.5, "carbs_g": 2.5, "fat_g": 7.8, "fiber_g": 0.5, "region": "Punjab"},
    {"name": "Tofu (raw)", "name_hindi": "टोफू", "category": "Proteins", "calories_per_100g": 76, "protein_g": 8.0, "carbs_g": 1.9, "fat_g": 4.8, "fiber_g": 0.3, "region": "Global"},
    {"name": "Dal Panchmel", "name_hindi": "पंचमेल दाल", "category": "Proteins", "calories_per_100g": 120, "protein_g": 7.5, "carbs_g": 16.5, "fat_g": 3.0, "fiber_g": 4.5, "region": "Rajasthan"},
    {"name": "Egg Bhurji", "name_hindi": "अंडा भुर्जी", "category": "Proteins", "calories_per_100g": 185, "protein_g": 12.8, "carbs_g": 3.5, "fat_g": 13.5, "fiber_g": 0.8, "region": "Pan-India"},
    {"name": "Butter Chicken", "name_hindi": "बटर चिकन", "category": "Proteins", "calories_per_100g": 210, "protein_g": 15.2, "carbs_g": 6.8, "fat_g": 13.5, "fiber_g": 0.5, "region": "Delhi/Punjab"},
    {"name": "Soya Chaap Curry", "name_hindi": "सोया चाप करी", "category": "Proteins", "calories_per_100g": 168, "protein_g": 12.5, "carbs_g": 11.2, "fat_g": 8.2, "fiber_g": 2.1, "region": "North India"},
    {"name": "Fish Fry", "name_hindi": "तली हुई मछली", "category": "Proteins", "calories_per_100g": 220, "protein_g": 18.5, "carbs_g": 8.0, "fat_g": 12.5, "fiber_g": 0.6, "region": "Coastal India"},
    {"name": "Keema Matar (Mutton)", "name_hindi": "कीमा मटर", "category": "Proteins", "calories_per_100g": 218, "protein_g": 19.2, "carbs_g": 5.5, "fat_g": 13.2, "fiber_g": 1.4, "region": "North India"}
]

def seed_database():
    app = create_app()
    with app.app_context():
        # Optional: clear existing foods
        # print("Clearing existing food items...")
        # FoodItem.query.delete()
        
        count = 0
        for f in foods:
            # Check if food already exists
            existing = FoodItem.query.filter_by(name=f["name"]).first()
            if not existing:
                food_item = FoodItem(
                    name=f["name"],
                    name_hindi=f["name_hindi"],
                    category=f["category"],
                    calories_per_100g=float(f["calories_per_100g"]),
                    protein_g=float(f["protein_g"]),
                    carbs_g=float(f["carbs_g"]),
                    fat_g=float(f["fat_g"]),
                    fiber_g=float(f["fiber_g"]),
                    region=f["region"],
                    is_verified=True,
                    source="manual"
                )
                db.session.add(food_item)
                count += 1
        
        db.session.commit()
        print(f"Successfully seeded {count} food items!")

if __name__ == "__main__":
    seed_database()
