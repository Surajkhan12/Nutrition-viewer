from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from dotenv import load_dotenv
import os
import time

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "nutrition.db")

app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "supersecret")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="threading"
)


class Food(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), unique=True, nullable=False)
    category = db.Column(db.String(50))

    calories = db.Column(db.String(50))
    protein = db.Column(db.String(50))
    carbs = db.Column(db.String(50))
    sugars = db.Column(db.String(50))
    fat = db.Column(db.String(50))
    fiber = db.Column(db.String(50))

    vitamins = db.Column(db.String(200))
    minerals = db.Column(db.String(200))

    water = db.Column(db.String(50))
    energy = db.Column(db.String(50))

    benefits = db.Column(db.String(500))
    uses = db.Column(db.String(500))
    when_to_eat = db.Column(db.String(500))


# 100 FRUITS
fruits_list = [
    ("Apple", "52 kcal", "0.3g", "13.8g", "10.4g", "0.2g", "2.4g", "86%", "52 kcal/100g", "Vitamin C, B6, K", "Potassium", "Boosts immunity, aids digestion", "Fresh eating, salads, juices", "Morning snack"),
    ("Banana", "89 kcal", "1.1g", "23g", "12g", "0.3g", "2.6g", "74%", "89 kcal/100g", "B6, C, B9", "Potassium, manganese", "High energy, heart health", "Smoothies, breakfast", "Pre/post workout"),
    ("Orange", "47 kcal", "0.9g", "11.8g", "9.3g", "0.1g", "2.4g", "87%", "47 kcal/100g", "Vitamin C, B9, A", "Calcium, potassium", "Boosts immunity, collagen", "Juices, fresh eating", "Morning breakfast"),
    ("Grapes", "67 kcal", "0.6g", "17g", "16.3g", "0.4g", "0.9g", "81%", "67 kcal/100g", "Vitamin C, K", "Copper, manganese", "Antioxidants, heart health", "Fresh eating, juices", "Afternoon snack"),
    ("Mango", "60 kcal", "0.8g", "15g", "13.7g", "0.4g", "1.6g", "83%", "60 kcal/100g", "Vitamin C, A, B6", "Copper, potassium", "Improves digestion, immunity", "Fresh eating, juices", "Summer season"),
    ("Pineapple", "50 kcal", "0.5g", "13.1g", "9.85g", "0.1g", "1.4g", "86%", "50 kcal/100g", "Vitamin C, B6", "Manganese, copper", "Aids digestion, anti-inflammatory", "Fresh eating, juices", "After meals"),
    ("Papaya", "43 kcal", "0.5g", "10.8g", "7.8g", "0.3g", "1.7g", "89%", "43 kcal/100g", "Vitamin C, A, B9", "Potassium, magnesium", "Aids digestion, immunity", "Fresh eating, smoothies", "Morning or evening"),
    ("Kiwi", "61 kcal", "1.1g", "14.7g", "6.2g", "0.5g", "3g", "84%", "61 kcal/100g", "Vitamin C, K, E", "Potassium, copper", "High fiber, sleep aid", "Fresh eating, smoothies", "Evening"),
    ("Strawberry", "32 kcal", "0.8g", "7.7g", "4.9g", "0.3g", "2g", "91%", "32 kcal/100g", "Vitamin C, K", "Manganese, copper", "Antioxidants, heart health", "Fresh eating, smoothies", "Anytime snack"),
    ("Blueberry", "57 kcal", "0.7g", "14.5g", "10g", "0.3g", "2.4g", "84%", "57 kcal/100g", "Vitamin C, K", "Copper, manganese", "Brain health, antioxidants", "Fresh eating, smoothies", "Morning breakfast"),
    ("Watermelon", "30 kcal", "0.6g", "7.6g", "6.2g", "0.2g", "0.4g", "92%", "30 kcal/100g", "Vitamin C, A", "Potassium, magnesium", "Hydration, heart health", "Fresh eating, juices", "Summer snack"),
    ("Peach", "39 kcal", "0.9g", "9.5g", "8.4g", "0.3g", "1.5g", "89%", "39 kcal/100g", "Vitamin C, A, K", "Potassium", "Skin health, digestion", "Fresh eating, juices", "Summer season"),
    ("Pear", "57 kcal", "0.4g", "15.2g", "9.8g", "0.1g", "3.1g", "84%", "57 kcal/100g", "Vitamin C, K, B9", "Copper, potassium", "High fiber, digestion", "Fresh eating, salads", "Afternoon snack"),
    ("Plum", "46 kcal", "0.7g", "11.4g", "9.9g", "0.3g", "1.4g", "85%", "46 kcal/100g", "Vitamin C, A, K", "Potassium, copper", "Aids digestion, bone health", "Fresh eating, dried", "Anytime snack"),
    ("Guava", "68 kcal", "2.6g", "14g", "8.9g", "0.9g", "5.4g", "81%", "68 kcal/100g", "Vitamin C, A, B9", "Copper, manganese", "High vitamin C, immune", "Fresh eating, juices", "Morning or evening"),
    ("Lychee", "66 kcal", "0.8g", "16.5g", "15.2g", "0.3g", "1.3g", "82%", "66 kcal/100g", "Vitamin C, B9", "Copper, manganese", "Immunity boost, circulation", "Fresh eating, desserts", "Summer season"),
    ("Pomegranate", "83 kcal", "1.7g", "18.7g", "13.7g", "1.2g", "4g", "78%", "83 kcal/100g", "Vitamin C, B5", "Copper, potassium", "Antioxidants, heart health", "Fresh eating, juices", "Fall/winter"),
    ("Dragon Fruit", "60 kcal", "1.2g", "13g", "8g", "0.4g", "1.9g", "85%", "60 kcal/100g", "Vitamin C, B", "Iron, magnesium", "Antioxidants, digestion", "Fresh eating, smoothies", "Anytime snack"),
    ("Lemon", "29 kcal", "1.1g", "9.3g", "2.5g", "0.3g", "2.8g", "89%", "29 kcal/100g", "Vitamin C", "Potassium, magnesium", "Detox, digestion, immunity", "Juices, beverages", "Morning with water"),
    ("Lime", "30 kcal", "0.7g", "10.5g", "1.7g", "0.2g", "2.8g", "88%", "30 kcal/100g", "Vitamin C", "Potassium, magnesium", "Immunity boost, detox", "Beverages, cooking", "Morning or with meals"),
    ("Pomelo", "38 kcal", "0.8g", "9g", "7g", "0.1g", "1g", "89%", "38 kcal/100g", "Vitamin C, B9", "Potassium, magnesium", "Immunity boost, low glycemic", "Fresh eating, juices", "Morning breakfast"),
    ("Grapefruit", "42 kcal", "0.8g", "10.7g", "6.9g", "0.1g", "1.6g", "88%", "42 kcal/100g", "Vitamin C, A", "Potassium, magnesium", "Weight loss, immunity", "Fresh eating, juices", "Morning breakfast"),
    ("Mandarin", "47 kcal", "0.7g", "12g", "9g", "0.3g", "1.8g", "88%", "47 kcal/100g", "Vitamin C, A", "Potassium, manganese", "Immunity boost, skin health", "Fresh eating, juices", "Afternoon snack"),
    ("Satsuma", "46 kcal", "0.7g", "12.2g", "9g", "0.3g", "1.8g", "88%", "46 kcal/100g", "Vitamin C, A", "Potassium, manganese", "Easy peel, high vitamin C", "Fresh eating, juices", "Afternoon snack"),
    ("Clementine", "47 kcal", "0.7g", "12g", "9g", "0.3g", "1.9g", "87%", "47 kcal/100g", "Vitamin C, A", "Potassium, manganese", "Small seedless, high vitamin C", "Fresh eating, juices", "Afternoon snack"),
    ("Blood Orange", "47 kcal", "0.9g", "11.8g", "9.3g", "0.1g", "2.4g", "87%", "47 kcal/100g", "Vitamin C, B9", "Calcium, potassium", "Deep antioxidants, unique", "Juices, fresh eating", "Morning breakfast"),
    ("Muskmelon", "34 kcal", "0.8g", "8.2g", "7.9g", "0.2g", "0.9g", "90%", "34 kcal/100g", "Vitamin A, C", "Potassium, magnesium", "Hydration, eye health", "Fresh eating, juices", "Summer snack"),
    ("Casaba", "35 kcal", "0.9g", "8.6g", "7.6g", "0.1g", "1.5g", "89%", "35 kcal/100g", "Vitamin C, B9", "Potassium, magnesium", "Sweet melon, hydration", "Fresh eating, juices", "Summer snack"),
    ("Blackcurrant", "63 kcal", "1.4g", "15.4g", "7.3g", "0.4g", "1.5g", "81%", "63 kcal/100g", "Vitamin C, K", "Copper, manganese", "Super antioxidant, immune", "Fresh eating, juices", "Anytime snack"),
    ("Gooseberry", "44 kcal", "0.9g", "10.2g", "7.2g", "0.4g", "2.7g", "88%", "44 kcal/100g", "Vitamin C, A", "Copper, potassium", "Sour and tangy, high vitamin C", "Fresh eating, jams", "Anytime snack"),
    ("Indian Gooseberry", "60 kcal", "0.9g", "13.7g", "7g", "0.6g", "4.3g", "82%", "60 kcal/100g", "Vitamin C, B9", "Copper, iron", "Super high vitamin C, immunity", "Fresh eating, juices", "Morning breakfast"),
    ("Langsat", "64 kcal", "0.9g", "15.6g", "14g", "0.2g", "0g", "82%", "64 kcal/100g", "Vitamin C", "Copper, manganese", "Tropical fruit, sweet", "Fresh eating, juices", "Afternoon snack"),
    ("Loquat", "47 kcal", "0.4g", "12.1g", "8.1g", "0.3g", "1.7g", "86%", "47 kcal/100g", "Vitamin A, C", "Copper, potassium", "Eye health, skin care", "Fresh eating, jams", "Spring season"),
    ("Medlar", "52 kcal", "0.4g", "13.5g", "6.1g", "0.3g", "6.3g", "84%", "52 kcal/100g", "Vitamin C, B9", "Copper, potassium", "Rare fruit, fiber-rich", "Cooked, jams, desserts", "Autumn season"),
    ("Bilberry", "57 kcal", "0.7g", "14.5g", "10g", "0.3g", "2.4g", "84%", "57 kcal/100g", "Vitamin C, K", "Copper, manganese", "Brain health, antioxidants", "Fresh eating, jams", "Summer season"),
    ("Red Currant", "56 kcal", "1.4g", "13.5g", "7.7g", "0.2g", "1.5g", "83%", "56 kcal/100g", "Vitamin C, K", "Copper, manganese", "Antioxidant berries, immunity", "Fresh eating, jams", "Summer season"),
    ("White Mulberry", "43 kcal", "1.4g", "8.8g", "6.5g", "0.4g", "1.7g", "88%", "43 kcal/100g", "Vitamin C, K", "Iron, potassium", "Sweet berries, digestion aid", "Fresh eating, jams", "Summer season"),
    ("Black Mulberry", "43 kcal", "1.4g", "8.8g", "6.5g", "0.4g", "1.7g", "88%", "43 kcal/100g", "Vitamin C, K", "Iron, potassium", "Dark berries, antioxidant", "Fresh eating, jams", "Summer season"),
    ("Ackee", "151 kcal", "2.2g", "8.5g", "3.9g", "13g", "2g", "71%", "151 kcal/100g", "B9, B5", "Copper, potassium", "National fruit of Jamaica", "Cooking, breakfast dishes", "Morning breakfast"),
    ("Alligator Pear", "160 kcal", "2g", "8.6g", "0.7g", "14.7g", "6.7g", "73%", "160 kcal/100g", "K, C, B5", "Potassium, copper", "Alternative name for avocado", "Salads, toast, smoothies", "Breakfast or lunch"),
    ("Elderberry", "73 kcal", "0.7g", "18.4g", "14.3g", "0.5g", "1g", "79%", "73 kcal/100g", "Vitamin C", "Potassium, copper", "Immune system support, antiviral", "Syrups, teas, juices", "During cold season"),
    ("Rhubarb", "21 kcal", "0.9g", "4.5g", "1.1g", "0.2g", "1.8g", "95%", "21 kcal/100g", "Vitamin K, C", "Calcium, potassium", "High fiber, laxative", "Cooked, pies, jams", "Spring season"),
    ("Baobab", "346 kcal", "2.3g", "87.5g", "21.2g", "0.3g", "44.7g", "9%", "346 kcal/100g", "B9, B5", "Iron, magnesium", "Super high fiber, immunity", "Powder, smoothies", "Anytime"),
    ("Feijoa", "44 kcal", "0.7g", "10.2g", "6.3g", "0.4g", "1.5g", "88%", "44 kcal/100g", "Vitamin C, B9", "Copper, potassium", "Tropical flavor, fiber-rich", "Fresh eating, smoothies", "Fall season"),
    ("Kiwi Berry", "61 kcal", "1.1g", "14.7g", "6.2g", "0.5g", "3g", "84%", "61 kcal/100g", "Vitamin C, K, E", "Potassium, copper", "Baby kiwi, high fiber", "Fresh eating, smoothies", "Evening snack"),
    ("Cape Gooseberry", "53 kcal", "1.9g", "11.2g", "6.3g", "0.16g", "2.4g", "85%", "53 kcal/100g", "Vitamin C, K", "Iron, potassium", "Ground cherry, sour-sweet", "Fresh eating, jams", "Anytime snack"),
    ("Ground Cherry", "53 kcal", "1.9g", "11.2g", "6.3g", "0.16g", "2.4g", "85%", "53 kcal/100g", "Vitamin C, K", "Iron, potassium", "Physalis fruit, tangy", "Fresh eating, jams", "Anytime snack"),
    ("Cupuacu", "40 kcal", "0.5g", "9.5g", "7g", "0.2g", "1.7g", "87%", "40 kcal/100g", "B9, B5", "Potassium, magnesium", "Amazonian fruit, antioxidant", "Fresh eating, smoothies", "Anytime snack"),
    ("Jabuticaba", "44 kcal", "1.1g", "10.5g", "8.5g", "0.2g", "2.7g", "87%", "44 kcal/100g", "Vitamin C, B9", "Copper, potassium", "Brazilian grape tree", "Fresh eating, jams", "Anytime snack"),
    ("Rose Apple", "30 kcal", "0.6g", "7.2g", "4.8g", "0.1g", "1.6g", "91%", "30 kcal/100g", "Vitamin C, A", "Potassium, copper", "Light and refreshing", "Fresh eating, juices", "Anytime snack"),
    ("Jambul", "82 kcal", "0.7g", "19.4g", "13g", "0.3g", "1.1g", "80%", "82 kcal/100g", "Vitamin C, B9", "Iron, potassium", "Black berry, blood sugar", "Fresh eating, juices", "Anytime snack"),
    ("Calamansi", "29 kcal", "1.1g", "9.3g", "2.5g", "0.3g", "2.8g", "89%", "29 kcal/100g", "Vitamin C", "Potassium, magnesium", "Filipino citrus, sour", "Juices, beverages", "Morning with water"),
    ("Monk Fruit", "17 kcal", "0.1g", "4.3g", "0g", "0g", "0g", "95%", "17 kcal/100g", "Vitamin C", "Potassium, sodium", "Zero sugar sweetener", "Sweetener, beverages", "Anytime"),
    ("Marula", "63 kcal", "1.3g", "15g", "11.4g", "0.4g", "1.9g", "83%", "63 kcal/100g", "Vitamin C, B9", "Copper, potassium", "African fruit, high vitamin C", "Fresh eating, juices", "Anytime snack"),
    ("Prickly Pear", "41 kcal", "0.7g", "9.6g", "6.4g", "0.5g", "3.7g", "88%", "41 kcal/100g", "Vitamin C, A", "Copper, magnesium", "Cactus fruit, detox", "Fresh eating, juices", "Anytime snack"),
    ("Longan", "60 kcal", "1.3g", "15.2g", "13.8g", "0.1g", "1.5g", "83%", "60 kcal/100g", "Vitamin C, B9", "Copper, potassium", "Dragon's eye, energy", "Fresh eating, dried", "Anytime snack"),
    ("Chebulic Myrobalan", "81 kcal", "0.5g", "21.5g", "19g", "0.5g", "0g", "78%", "81 kcal/100g", "Vitamin C", "Potassium, copper", "Ayurvedic fruit, digestion", "Fresh eating, supplements", "Anytime"),
    ("Barberry", "25 kcal", "0.4g", "6.3g", "4.8g", "0.3g", "0g", "85%", "25 kcal/100g", "Vitamin C, K", "Copper, iron", "Tart berry, antioxidant", "Dried, juices, spice", "Anytime"),
    ("Pepino", "20 kcal", "0.8g", "4.2g", "3.6g", "0.1g", "0.7g", "94%", "20 kcal/100g", "Vitamin C, B9", "Potassium, magnesium", "Melon pear, hydration", "Fresh eating, juices", "Anytime snack"),
    ("Horned Melon", "44 kcal", "0.8g", "7.6g", "3.4g", "0.3g", "2.5g", "88%", "44 kcal/100g", "Vitamin C", "Copper, magnesium", "Kiwano, unique texture", "Fresh eating, salads", "Anytime snack"),
    ("Ackee Fruit", "151 kcal", "2.2g", "8.5g", "3.9g", "13g", "2g", "71%", "151 kcal/100g", "B9, B5", "Copper, potassium", "Caribbean staple", "Cooking, breakfast", "Morning breakfast"),
    ("Coconut", "354 kcal", "3.3g", "15.2g", "9g", "33.5g", "9g", "47%", "354 kcal/100g", "B9, B5", "Manganese, copper", "High energy, brain health", "Fresh eating, oil", "Morning or supplement"),
    ("Avocado", "160 kcal", "2g", "8.6g", "0.7g", "14.7g", "6.7g", "73%", "160 kcal/100g", "K, C, B5", "Potassium, copper", "Heart health, healthy fats", "Salads, toast, smoothies", "Breakfast or lunch"),
    ("Cherry", "63 kcal", "1.1g", "16g", "12.8g", "0.2g", "2.1g", "82%", "63 kcal/100g", "Vitamin C, A", "Copper, manganese", "Anti-inflammatory, sleep", "Fresh eating, desserts", "Evening for sleep"),
    ("Raspberry", "52 kcal", "1.2g", "12g", "4.4g", "0.7g", "6.5g", "86%", "52 kcal/100g", "Vitamin C, K", "Manganese, copper", "High fiber, antioxidants", "Fresh eating, smoothies", "Anytime snack"),
    ("Blackberry", "43 kcal", "1.4g", "10g", "4.9g", "0.5g", "5.3g", "88%", "43 kcal/100g", "Vitamin C, K", "Manganese, copper", "Antioxidants, heart health", "Fresh eating, smoothies", "Anytime snack"),
    ("Fig", "74 kcal", "0.8g", "19g", "16.3g", "0.3g", "1.5g", "80%", "74 kcal/100g", "B6, B9", "Calcium, iron, potassium", "Aids digestion, bone health", "Fresh eating, dried", "Anytime snack"),
    ("Date", "282 kcal", "2.7g", "75g", "66.5g", "0.4g", "6.7g", "21%", "282 kcal/100g", "B9, B6", "Copper, magnesium", "High energy, natural sweetener", "Desserts, smoothies", "Pre-workout energy"),
    ("Apricot", "48 kcal", "1.4g", "11.1g", "9.2g", "0.4g", "2g", "86%", "48 kcal/100g", "Vitamin A, C", "Potassium, copper", "Eye health, skin care", "Fresh eating, dried", "Anytime snack"),
    ("Cranberry", "46 kcal", "0.4g", "12.2g", "4g", "0.1g", "4.6g", "87%", "46 kcal/100g", "Vitamin C, K", "Copper, manganese", "Urinary health, antioxidants", "Juices, sauces, dried", "Anytime snack"),
    ("Passion Fruit", "97 kcal", "2.2g", "23.4g", "11.2g", "0.7g", "10.4g", "73%", "97 kcal/100g", "Vitamin C, A", "Iron, magnesium, copper", "High fiber, digestion, sleep", "Fresh pulp, juices", "Evening snack"),
    ("Tangerine", "47 kcal", "0.7g", "12g", "9g", "0.3g", "1.8g", "88%", "47 kcal/100g", "Vitamin C, A", "Potassium, manganese", "Immunity boost, skin health", "Fresh eating, juices", "Morning breakfast"),
    ("Persimmon", "81 kcal", "0.6g", "20.6g", "18.6g", "0.3g", "3.6g", "80%", "81 kcal/100g", "Vitamin A, C", "Potassium, copper", "Eye health, antioxidants", "Fresh eating, desserts", "Autumn season"),
    ("Cantaloupe", "34 kcal", "0.8g", "8.2g", "7.9g", "0.2g", "0.9g", "90%", "34 kcal/100g", "Vitamin A, C", "Potassium, magnesium", "Hydration, eye health", "Fresh eating, juices", "Summer snack"),
    ("Honeydew", "36 kcal", "0.5g", "8.9g", "8g", "0.1g", "1.4g", "90%", "36 kcal/100g", "Vitamin C, B9", "Potassium, magnesium", "Hydration, sleep aid", "Fresh eating, juices", "Summer season"),
]

# 100 VEGETABLES
vegetables_list = [
    ("Broccoli", "34 kcal", "2.8g", "6.6g", "1.2g", "0.4g", "2.4g", "90%", "34 kcal/100g", "Vitamin C, K, A", "Chromium, potassium", "Cancer prevention, bone health", "Steamed, roasted, raw", "Lunch or dinner"),
    ("Carrot", "41 kcal", "0.9g", "9.6g", "4.7g", "0.2g", "2.8g", "88%", "41 kcal/100g", "Vitamin A, K, B9", "Potassium, manganese", "Eye health, immune boost", "Raw, cooked, juices", "Anytime"),
    ("Spinach", "23 kcal", "2.7g", "3.6g", "0.4g", "0.4g", "2.2g", "91%", "23 kcal/100g", "Vitamin K, A, C", "Iron, calcium, magnesium", "Iron-rich, bone health", "Salads, smoothies, cooking", "Lunch or dinner"),
    ("Cucumber", "16 kcal", "0.7g", "3.6g", "1.7g", "0.1g", "0.5g", "96%", "16 kcal/100g", "Vitamin K, C", "Potassium, manganese", "Hydration, weight loss", "Raw salads, juices", "Lunch or snack"),
    ("Tomato", "18 kcal", "0.9g", "3.9g", "2.3g", "0.2g", "1.2g", "95%", "18 kcal/100g", "Vitamin C, K, A", "Potassium, manganese", "Heart health, immunity", "Salads, sauces, cooking", "Lunch or dinner"),
    ("Potato", "77 kcal", "2g", "17.5g", "0.7g", "0.1g", "2.1g", "79%", "77 kcal/100g", "B6, C, B9", "Potassium, manganese", "Energy boost, satiety", "Boiled, baked, roasted", "Lunch or dinner"),
    ("Onion", "40 kcal", "1.1g", "9g", "4.2g", "0.1g", "1.7g", "89%", "40 kcal/100g", "Vitamin C, B9", "Potassium, manganese", "Antioxidants, heart health", "Cooking, raw salads", "Lunch or dinner"),
    ("Garlic", "149 kcal", "6.4g", "33.1g", "1g", "0.5g", "2.1g", "59%", "149 kcal/100g", "Vitamin C, B6", "Manganese, potassium", "Antibacterial, immunity", "Cooking, raw, supplements", "Lunch or dinner"),
    ("Beetroot", "43 kcal", "1.6g", "9.6g", "6.8g", "0.2g", "2.8g", "87%", "43 kcal/100g", "Folate, B9, B6", "Potassium, manganese", "Blood pressure, detox", "Salads, juices, roasted", "Lunch or dinner"),
    ("Bell Pepper", "31 kcal", "1g", "6g", "3.2g", "0.3g", "2.2g", "92%", "31 kcal/100g", "Vitamin C, A, B6", "Potassium, manganese", "High vitamin C, antioxidants", "Salads, cooking, roasted", "Lunch or dinner"),
    ("Cauliflower", "25 kcal", "1.9g", "4.9g", "0.9g", "0.4g", "2.4g", "92%", "25 kcal/100g", "Vitamin C, K, B9", "Potassium, chromium", "Cancer prevention, detox", "Roasted, steamed, raw", "Lunch or dinner"),
    ("Cabbage", "25 kcal", "1.3g", "5.8g", "1g", "0.1g", "2.4g", "92%", "25 kcal/100g", "Vitamin K, C", "Potassium, manganese", "Gut health, anti-inflammatory", "Coleslaw, soups, cooking", "Lunch or dinner"),
    ("Green Beans", "31 kcal", "1.9g", "7g", "1.9g", "0.1g", "2.7g", "90%", "31 kcal/100g", "Vitamin K, C", "Iron, potassium", "Protein-rich, digestion", "Cooking, salads, soups", "Lunch or dinner"),
    ("Peas", "81 kcal", "5.4g", "14.4g", "5.7g", "0.4g", "2.6g", "79%", "81 kcal/100g", "Vitamin K, C, B6", "Potassium, manganese", "Protein-rich, energy boost", "Cooking, soups, salads", "Lunch or dinner"),
    ("Sweet Potato", "86 kcal", "1.6g", "20.1g", "4.2g", "0.1g", "3g", "77%", "86 kcal/100g", "Vitamin A, C, B6", "Potassium, manganese", "Eye health, energy", "Roasted, baked, mashed", "Lunch or dinner"),
    ("Celery", "16 kcal", "0.7g", "3.2g", "1.3g", "0.2g", "1.6g", "95%", "16 kcal/100g", "Vitamin K, C", "Potassium, manganese", "Low calorie, hydration", "Raw salads, juices, soups", "Anytime snack"),
    ("Lettuce", "15 kcal", "1.2g", "2.9g", "0.8g", "0.3g", "1.3g", "95%", "15 kcal/100g", "Vitamin K, A", "Folate, potassium", "Low calorie, weight loss", "Salads, wraps, raw", "Lunch or anytime"),
    ("Kale", "49 kcal", "4.3g", "8.7g", "0.6g", "0.9g", "1.3g", "84%", "49 kcal/100g", "Vitamin K, A, C", "Calcium, iron, potassium", "Superfood, detoxification", "Salads, smoothies, chips", "Lunch or dinner"),
    ("Zucchini", "21 kcal", "1.4g", "3.7g", "1.2g", "0.4g", "1.1g", "95%", "21 kcal/100g", "Vitamin C, B9", "Potassium, manganese", "Low calorie, weight loss", "Cooking, grilled, noodles", "Lunch or dinner"),
    ("Mushroom", "22 kcal", "3.1g", "3.3g", "0.1g", "0.3g", "1g", "92%", "22 kcal/100g", "B5, D", "Selenium, potassium", "Immune boost, vitamin D", "Cooking, salads, soups", "Lunch or dinner"),
    ("Eggplant", "25 kcal", "0.9g", "5.9g", "3.5g", "0.2g", "3g", "92%", "25 kcal/100g", "B9, C", "Potassium, manganese", "Antioxidants, heart health", "Grilled, fried, baked", "Lunch or dinner"),
    ("Asparagus", "20 kcal", "2.2g", "3.7g", "1.9g", "0.1g", "2.1g", "93%", "20 kcal/100g", "Vitamin K, A, C", "Chromium, potassium", "High fiber, diuretic", "Grilled, steamed, roasted", "Lunch or dinner"),
    ("Artichoke", "47 kcal", "3.3g", "10.5g", "0.2g", "0.2g", "5.2g", "84%", "47 kcal/100g", "B9, C", "Iron, potassium", "Liver health, antioxidants", "Steamed, roasted, baked", "Lunch or dinner"),
    ("Radish", "16 kcal", "0.7g", "3.4g", "1.9g", "0.1g", "1.6g", "95%", "16 kcal/100g", "Vitamin C", "Potassium, manganese", "Detoxification, low calorie", "Raw salads, pickled", "Lunch or snack"),
    ("Turnip", "36 kcal", "1.1g", "8g", "4.6g", "0.1g", "1.8g", "92%", "36 kcal/100g", "Vitamin C, B9", "Potassium, manganese", "Low calorie, bone health", "Roasted, boiled, soups", "Lunch or dinner"),
    ("Parsnip", "75 kcal", "1.2g", "17.9g", "4.8g", "0.3g", "4.9g", "79%", "75 kcal/100g", "Vitamin C, B9", "Potassium, manganese", "High fiber, digestion", "Roasted, boiled, fries", "Lunch or dinner"),
    ("Okra", "33 kcal", "1.9g", "7.5g", "1.5g", "0.2g", "3.3g", "90%", "33 kcal/100g", "Vitamin K, C", "Potassium, magnesium", "High fiber, digestion", "Cooking, stir-fry, curries", "Lunch or dinner"),
    ("Leek", "61 kcal", "1.5g", "14.2g", "2.3g", "0.3g", "1.8g", "83%", "61 kcal/100g", "Vitamin K, C", "Copper, iron", "Bone health, antioxidants", "Cooking, soups, baking", "Lunch or dinner"),
    ("Chives", "30 kcal", "3.3g", "4.4g", "0.1g", "0.7g", "2.1g", "91%", "30 kcal/100g", "Vitamin K, C", "Copper, iron", "Flavor booster, antioxidants", "Garnish, cooking, salads", "Lunch or dinner"),
    ("Dill", "43 kcal", "3.5g", "7g", "0.1g", "1.2g", "2.1g", "85%", "43 kcal/100g", "Vitamin A, C", "Calcium, iron", "Digestive aid, flavor", "Seasoning, cooking, pickling", "Lunch or dinner"),
    ("Basil", "23 kcal", "3.2g", "2.7g", "0.3g", "0.6g", "1.6g", "92%", "23 kcal/100g", "Vitamin K, A", "Calcium, iron", "Anti-inflammatory, antibacterial", "Cooking, salads, pesto", "Lunch or dinner"),
    ("Parsley", "36 kcal", "2.7g", "6.3g", "0.4g", "0.8g", "3.3g", "88%", "36 kcal/100g", "Vitamin K, C, A", "Iron, calcium", "Detoxification, anti-inflammatory", "Garnish, cooking, salads", "Lunch or dinner"),
    ("Mint", "70 kcal", "3.8g", "14.9g", "0.3g", "0.9g", "8g", "78%", "70 kcal/100g", "Vitamin A, C", "Copper, manganese", "Digestive aid, cooling", "Beverages, cooking, teas", "Anytime"),
    ("Thyme", "101 kcal", "5.6g", "24.5g", "0.3g", "1.7g", "18.4g", "65%", "101 kcal/100g", "Vitamin C, A", "Iron, manganese", "Cough relief, antioxidants", "Cooking, teas, seasoning", "Lunch or dinner"),
    ("Ginger", "80 kcal", "1.8g", "17.8g", "1.7g", "0.8g", "2.4g", "79%", "80 kcal/100g", "B5, B6", "Manganese, copper", "Anti-inflammatory, nausea", "Cooking, teas, marinades", "With meals"),
    ("Chili Pepper", "40 kcal", "1.9g", "8.8g", "5.3g", "0.4g", "1.5g", "88%", "40 kcal/100g", "Vitamin C, A", "Potassium, manganese", "Metabolism boost, immunity", "Cooking, sauces, spice", "Lunch or dinner"),
    ("Black Pepper", "251 kcal", "10.4g", "64.8g", "0.6g", "3.3g", "25.3g", "12%", "251 kcal/100g", "B5, C", "Iron, manganese", "Nutrient absorption, anti-inflammatory", "Seasoning, cooking, spice", "Lunch or dinner"),
    ("Turmeric", "312 kcal", "9.7g", "67.1g", "3.2g", "3.1g", "21g", "13%", "312 kcal/100g", "B6, B9", "Iron, manganese", "Anti-inflammatory, antioxidants", "Cooking, lattes, curries", "Lunch or dinner"),
    ("Coriander", "298 kcal", "12.4g", "54.9g", "1g", "17.8g", "41.9g", "9%", "298 kcal/100g", "K, B9", "Iron, manganese", "Digestion aid, anti-inflammatory", "Cooking, seasoning, chutney", "Lunch or dinner"),
    ("Watercress", "11 kcal", "2.3g", "0.4g", "0g", "0.1g", "0.5g", "95%", "11 kcal/100g", "Vitamin K, C", "Copper, iron", "Lung health, cancer prevention", "Salads, soups, smoothies", "Lunch or anytime"),
    ("Fennel", "31 kcal", "1.2g", "7.3g", "3.2g", "0.2g", "3.1g", "90%", "31 kcal/100g", "Vitamin C, B9", "Potassium, manganese", "Digestive aid, flavor", "Cooking, raw, teas", "After meals"),
    ("Celery Root", "42 kcal", "1.5g", "9.2g", "1g", "0.2g", "1.8g", "88%", "42 kcal/100g", "Vitamin C, B9", "Potassium, manganese", "Low calorie, heart health", "Roasted, mashed, soups", "Lunch or dinner"),
    ("Beet Greens", "23 kcal", "2.2g", "4.3g", "0.3g", "0.2g", "2.1g", "91%", "23 kcal/100g", "Vitamin K, A, C", "Iron, calcium", "Nutrient-dense, iron-rich", "Salads, smoothies, cooking", "Lunch or dinner"),
    ("Bok Choy", "13 kcal", "1.5g", "2.2g", "0.4g", "0.2g", "1.2g", "95%", "13 kcal/100g", "Vitamin K, C, A", "Calcium, iron", "Calcium-rich, bone health", "Stir-fry, soups, raw", "Lunch or dinner"),
    ("Tatsoi", "22 kcal", "2.1g", "3.8g", "0.6g", "0.3g", "1.5g", "93%", "22 kcal/100g", "Vitamin K, A, C", "Iron, calcium", "Asian green, calcium-rich", "Stir-fry, soups, salads", "Lunch or dinner"),
    ("Mustard Greens", "27 kcal", "2.7g", "4.7g", "0.5g", "0.6g", "2.2g", "91%", "27 kcal/100g", "Vitamin K, A, C", "Iron, calcium", "Spicy greens, calcium-rich", "Cooking, salads, pickling", "Lunch or dinner"),
    ("Collard Greens", "33 kcal", "3.6g", "4.3g", "0.3g", "0.6g", "4g", "91%", "33 kcal/100g", "Vitamin K, A, C", "Calcium, iron", "Southern staple, calcium-rich", "Cooking, soups, salads", "Lunch or dinner"),
    ("Swiss Chard", "19 kcal", "1.8g", "3.7g", "0.4g", "0.2g", "1.6g", "92%", "19 kcal/100g", "Vitamin K, A, C", "Iron, magnesium", "Rainbow chard, mineral-rich", "Cooking, salads, juices", "Lunch or dinner"),
    ("Endive", "17 kcal", "1.3g", "3.4g", "0.6g", "0.2g", "3.1g", "94%", "17 kcal/100g", "Vitamin K, C", "Folate, potassium", "Bitter greens, fiber-rich", "Salads, cooking, raw", "Lunch or dinner"),
    ("Escarole", "17 kcal", "1.3g", "3.4g", "0.6g", "0.2g", "3.1g", "94%", "17 kcal/100g", "Vitamin K, C", "Folate, potassium", "Bitter leafy green, antioxidant", "Salads, cooking, raw", "Lunch or dinner"),
    ("Radicchio", "23 kcal", "1.3g", "4.5g", "0.6g", "0.1g", "0.7g", "93%", "23 kcal/100g", "Vitamin K, C", "Copper, potassium", "Red leafy, bitter, antioxidant", "Salads, cooking, grilled", "Lunch or dinner"),
    ("Chicory", "23 kcal", "1.7g", "4.7g", "0.2g", "0.1g", "0.9g", "93%", "23 kcal/100g", "Vitamin K, C", "Copper, potassium", "Root vegetable, prebiotic", "Roasted, coffee substitute", "Lunch or dinner"),
    ("Arugula", "25 kcal", "2.6g", "3.7g", "0.4g", "0.7g", "1.6g", "92%", "25 kcal/100g", "Vitamin K, C, A", "Calcium, potassium", "Peppery green, calcium-rich", "Salads, pesto, cooking", "Lunch or dinner"),
    ("Brussels Sprouts", "34 kcal", "2.8g", "6.9g", "1.2g", "0.4g", "2.4g", "88%", "34 kcal/100g", "Vitamin C, K", "Chromium, potassium", "Cancer prevention, detox", "Roasted, steamed, soups", "Lunch or dinner"),
    ("Kohlrabi", "27 kcal", "1.7g", "6.2g", "3.2g", "0.1g", "1.2g", "91%", "27 kcal/100g", "Vitamin C, B9", "Potassium, manganese", "Cabbage relative, crunchy", "Raw, cooked, roasted", "Lunch or dinner"),
    ("Romanesco", "31 kcal", "2.9g", "5.8g", "1.2g", "0.4g", "2.3g", "91%", "31 kcal/100g", "Vitamin C, K", "Potassium, chromium", "Fractal vegetable, unique", "Raw, roasted, steamed", "Lunch or dinner"),
    ("Tomatillo", "32 kcal", "1.1g", "5.8g", "1.3g", "1.2g", "1.9g", "92%", "32 kcal/100g", "Vitamin C, B9", "Potassium, copper", "Green tomato cousin, tangy", "Salsa, cooking, raw", "Lunch or dinner"),
    ("Heirloom Tomato", "18 kcal", "0.9g", "3.9g", "2.3g", "0.2g", "1.2g", "95%", "18 kcal/100g", "Vitamin C, K", "Potassium, manganese", "Heritage variety, rich flavor", "Salads, sauces, cooking", "Lunch or dinner"),
    ("Green Tomato", "23 kcal", "1g", "5g", "0.5g", "0.2g", "0.9g", "94%", "23 kcal/100g", "Vitamin C", "Potassium, calcium", "Tangy, lower lycopene", "Fried, pickled, cooking", "Lunch or dinner"),
    ("Roma Tomato", "18 kcal", "0.9g", "3.9g", "2.3g", "0.2g", "1.2g", "95%", "18 kcal/100g", "Vitamin C, K", "Potassium, manganese", "Plum type, dense", "Sauces, cooking, canning", "Lunch or dinner"),
    ("Cherry Tomato", "27 kcal", "1.2g", "5.8g", "3.7g", "0.3g", "1.5g", "91%", "27 kcal/100g", "Vitamin C, K", "Potassium, manganese", "Sweet variety, snackable", "Salads, raw snacks, pasta", "Lunch or anytime"),
    ("Grape Tomato", "27 kcal", "1.2g", "5.8g", "3.7g", "0.3g", "1.5g", "91%", "27 kcal/100g", "Vitamin C, K", "Potassium, manganese", "Oblong shape, sweet", "Salads, raw snacks, pasta", "Lunch or anytime"),
    ("Yellow Tomato", "18 kcal", "0.9g", "3.9g", "2.3g", "0.2g", "1.2g", "95%", "18 kcal/100g", "Vitamin C, K", "Potassium, manganese", "Mild flavor, low acidity", "Salads, sauces, cooking", "Lunch or dinner"),
    ("Pattypan Squash", "19 kcal", "1.5g", "3.5g", "1.5g", "0.3g", "1g", "94%", "19 kcal/100g", "Vitamin C, B9", "Potassium, manganese", "UFO-shaped, mild", "Roasted, grilled, stuffed", "Lunch or dinner"),
    ("Yellow Squash", "21 kcal", "1.4g", "3.7g", "1.2g", "0.4g", "1.1g", "95%", "21 kcal/100g", "Vitamin C, B9", "Potassium, manganese", "Summer squash, mild", "Cooking, grilled, noodles", "Lunch or dinner"),
    ("Delicata Squash", "36 kcal", "0.7g", "8.3g", "2.1g", "0.5g", "1.1g", "89%", "36 kcal/100g", "Vitamin A, C", "Potassium, manganese", "Sweet squash, edible skin", "Roasted, baked, stuffed", "Lunch or dinner"),
    ("Acorn Squash", "56 kcal", "1.1g", "14.9g", "4.2g", "0.1g", "2.3g", "84%", "56 kcal/100g", "Vitamin A, C", "Potassium, manganese", "Nutty flavor, rich", "Roasted, baked, stuffed", "Lunch or dinner"),
    ("Butternut Squash", "45 kcal", "1g", "11.2g", "2.2g", "0.1g", "2g", "87%", "45 kcal/100g", "Vitamin A, C", "Potassium, manganese", "Sweet, creamy", "Roasted, soups, mashed", "Lunch or dinner"),
    ("Spaghetti Squash", "31 kcal", "0.7g", "7g", "3.9g", "0.6g", "1.4g", "92%", "31 kcal/100g", "Vitamin C, B9", "Potassium, manganese", "Low carb pasta", "Baked, noodles, salads", "Lunch or dinner"),
    ("Kabocha Squash", "54 kcal", "1g", "12.9g", "4.1g", "0.1g", "2.3g", "86%", "54 kcal/100g", "Vitamin A, C", "Potassium, manganese", "Japanese pumpkin, sweet", "Roasted, soups, mashed", "Lunch or dinner"),
    ("Purple Cabbage", "31 kcal", "1.4g", "7.2g", "1.2g", "0.2g", "2.1g", "90%", "31 kcal/100g", "Vitamin K, C", "Potassium, manganese", "Anthocyanins, antioxidant", "Coleslaw, soups, cooking", "Lunch or dinner"),
    ("Red Onion", "40 kcal", "1.1g", "9g", "4.2g", "0.1g", "1.7g", "89%", "40 kcal/100g", "Vitamin C, B9", "Potassium, manganese", "Anthocyanins, antioxidant", "Cooking, raw salads, soups", "Lunch or dinner"),
    ("Golden Beet", "43 kcal", "1.6g", "9.6g", "6.8g", "0.2g", "2.8g", "87%", "43 kcal/100g", "Folate, B9", "Potassium, manganese", "Milder than red beet", "Salads, juices, roasted", "Lunch or dinner"),
    ("Candy Cane Beet", "43 kcal", "1.6g", "9.6g", "6.8g", "0.2g", "2.8g", "87%", "43 kcal/100g", "Folate, B9", "Potassium, manganese", "Striped variety, unique", "Salads, juices, roasted", "Lunch or dinner"),
]

# 100 DRY FRUITS
dryfruits_list = [
    ("Walnut", "654 kcal", "9.1g", "13.7g", "2.6g", "65.2g", "6.7g", "4%", "654 kcal/100g", "B7, B9", "Copper, manganese", "Brain health, omega-3 rich", "Raw eating, baking, salads", "Morning or pre-workout"),
    ("Almond", "579 kcal", "21.2g", "21.6g", "4.4g", "49.9g", "12.5g", "4%", "579 kcal/100g", "B7, E", "Manganese, magnesium", "High protein, bone health", "Raw eating, butter, baking", "Morning snack"),
    ("Cashew", "553 kcal", "18.2g", "30.2g", "5.9g", "43.9g", "3.3g", "5%", "553 kcal/100g", "K, B9", "Copper, magnesium", "Heart health, iron-rich", "Raw eating, butter, cooking", "Afternoon snack"),
    ("Raisin", "299 kcal", "3.1g", "79.5g", "59.9g", "0.3g", "3.7g", "15%", "299 kcal/100g", "B9, B6", "Copper, iron", "Energy boost, bone health", "Eating, baking, cereals", "Anytime snack"),
    ("Pistachio", "557 kcal", "20.2g", "27.7g", "7.7g", "45.4g", "10.6g", "4%", "557 kcal/100g", "K, B9", "Copper, manganese", "Heart health, blood sugar", "Raw eating, baking, salads", "Afternoon snack"),
    ("Hazelnut", "628 kcal", "14.9g", "16.7g", "4.3g", "60.8g", "9.7g", "5%", "628 kcal/100g", "B7, E", "Copper, manganese", "Heart health, antioxidants", "Raw eating, baking, oils", "Morning snack"),
    ("Pecan", "691 kcal", "9.2g", "13.9g", "3.9g", "71.9g", "8.7g", "3%", "691 kcal/100g", "B7, B1", "Manganese, copper", "Brain health, antioxidants", "Raw eating, baking, pies", "Afternoon snack"),
    ("Apricot (Dried)", "241 kcal", "3.4g", "62.6g", "53.4g", "0.5g", "7.3g", "31%", "241 kcal/100g", "A, B9", "Copper, potassium", "Energy boost, eye health", "Eating, baking, smoothies", "Afternoon snack"),
    ("Date (Dried)", "282 kcal", "2.7g", "75g", "66.5g", "0.4g", "6.7g", "21%", "282 kcal/100g", "B9, B6", "Copper, magnesium", "Natural energy, digestion", "Eating, smoothies, energy bars", "Pre-workout energy"),
    ("Fig (Dried)", "249 kcal", "3.3g", "63.9g", "47.7g", "0.9g", "9.8g", "20%", "249 kcal/100g", "B6, B9", "Calcium, iron", "Bone health, digestion", "Eating, baking, smoothies", "Afternoon snack"),
    ("Prune", "240 kcal", "2.2g", "63.9g", "38.1g", "0.4g", "7.1g", "28%", "240 kcal/100g", "K, B9", "Copper, potassium", "Digestion aid, bone health", "Eating, baking, smoothies", "Evening for digestion"),
    ("Cranberry (Dried)", "308 kcal", "0.6g", "82g", "67g", "0.2g", "5.1g", "15%", "308 kcal/100g", "C, B9", "Copper, manganese", "Urinary health, antioxidant", "Eating, baking, cereals", "Anytime snack"),
    ("Coconut (Dried)", "660 kcal", "7.3g", "24.2g", "9g", "64.5g", "9g", "3%", "660 kcal/100g", "B9, B5", "Manganese, copper", "High energy, brain health", "Eating, baking, milk", "Morning or afternoon"),
    ("Pumpkin Seeds", "541 kcal", "24.5g", "53.7g", "1.3g", "20.3g", "1.7g", "5%", "541 kcal/100g", "B9, B5", "Copper, manganese", "Prostate health, sleep aid", "Raw eating, roasted, baking", "Evening for sleep"),
    ("Sunflower Seeds", "584 kcal", "20.9g", "20.5g", "2.6g", "51.5g", "8.6g", "4%", "584 kcal/100g", "B5, E", "Copper, selenium", "Heart health, immune boost", "Raw eating, roasted, baking", "Afternoon snack"),
    ("Hemp Seeds", "567 kcal", "31.6g", "12.3g", "1.5g", "48.3g", "1.2g", "4%", "567 kcal/100g", "B1, B2", "Iron, manganese", "Complete protein, omega-3", "Eating, smoothies, salads", "Morning breakfast"),
    ("Chia Seeds", "486 kcal", "16.5g", "42.1g", "0g", "30.7g", "34.4g", "6%", "486 kcal/100g", "B1, B2", "Copper, magnesium", "Super high fiber, omega-3", "Pudding, smoothies, baking", "Morning breakfast"),
    ("Flax Seeds", "534 kcal", "18.3g", "28.9g", "1.6g", "42.2g", "27.3g", "7%", "534 kcal/100g", "B1, B6", "Copper, manganese", "Omega-3 rich, digestion", "Ground, smoothies, baking", "Morning breakfast"),
    ("Sesame Seeds", "565 kcal", "17.7g", "26.7g", "0.3g", "48g", "11.8g", "5%", "565 kcal/100g", "B1, B2", "Copper, calcium", "Calcium-rich, bone health", "Eating, tahini, baking", "Anytime"),
    ("Pine Nuts", "673 kcal", "13.7g", "13.1g", "3.6g", "68.4g", "3.7g", "3%", "673 kcal/100g", "B1, B5", "Copper, manganese", "Brain health, immunity", "Raw eating, pesto, baking", "Afternoon snack"),
    ("Macadamia Nuts", "718 kcal", "7.9g", "13.8g", "4.6g", "75.8g", "8.6g", "1%", "718 kcal/100g", "B1, B9", "Manganese, copper", "Heart health, healthy", "Raw eating, butter, baking", "Afternoon snack"),
    ("Brazil Nuts", "656 kcal", "14.3g", "12.3g", "2.3g", "66.4g", "6.5g", "3%", "656 kcal/100g", "B1, B9", "Selenium, copper", "Selenium-rich, thyroid", "Raw eating, baking, oils", "Few per day"),
    ("Chestnut", "213 kcal", "1.6g", "45.5g", "11.8g", "2g", "8.8g", "50%", "213 kcal/100g", "B9, C", "Copper, manganese", "Low fat nut, satiety", "Roasted, baking, soups", "Afternoon snack"),
    ("Goji Berry", "349 kcal", "14.3g", "77.1g", "48.3g", "1.5g", "13g", "6%", "349 kcal/100g", "A, C, B9", "Iron, copper", "Antioxidants, immune boost", "Eating, smoothies, teas", "Morning or afternoon"),
    ("Dried Mango", "322 kcal", "3.3g", "80g", "71g", "0.2g", "1.6g", "15%", "322 kcal/100g", "A, C", "Copper, potassium", "Energy boost, skin health", "Eating, baking, smoothies", "Afternoon snack"),
    ("Dried Papaya", "305 kcal", "0.8g", "77.8g", "64.6g", "0.3g", "1.8g", "19%", "305 kcal/100g", "A, C", "Potassium, magnesium", "Enzyme-rich, digestion", "Eating, smoothies, baking", "Afternoon snack"),
    ("Dried Pineapple", "286 kcal", "0.4g", "73g", "64g", "0.5g", "0.8g", "19%", "286 kcal/100g", "C, B6", "Manganese, copper", "Enzyme-rich, sweet treat", "Eating, smoothies, baking", "Afternoon snack"),
    ("Dried Blueberry", "317 kcal", "1.4g", "80.5g", "59.5g", "0.5g", "3.9g", "16%", "317 kcal/100g", "C, K", "Copper, manganese", "Antioxidants, brain health", "Eating, smoothies, cereals", "Morning breakfast"),
    ("Dried Strawberry", "330 kcal", "3.7g", "82.3g", "60.5g", "1.2g", "4.8g", "12%", "330 kcal/100g", "C, K", "Manganese, copper", "Antioxidants, immunity", "Eating, smoothies, cereals", "Anytime"),
    ("Dried Banana", "346 kcal", "1.5g", "88.3g", "47.3g", "0.3g", "2.1g", "9%", "346 kcal/100g", "B6, B9", "Potassium, manganese", "Energy boost, sweet treat", "Eating, smoothies, cereals", "Pre-workout energy"),
    ("Dried Cranberry", "308 kcal", "0.6g", "82g", "67g", "0.2g", "5.1g", "15%", "308 kcal/100g", "C, B9", "Copper, manganese", "Urinary health, antioxidant", "Eating, baking, sauces", "Anytime snack"),
    ("Dried Apple", "243 kcal", "0.4g", "65g", "60g", "0.3g", "4.2g", "32%", "243 kcal/100g", "C, B9", "Copper, potassium", "Fiber-rich, sweet treat", "Eating, baking, smoothies", "Afternoon snack"),
    ("Dried Kiwi", "338 kcal", "4.1g", "81.4g", "59.5g", "2g", "8.8g", "8%", "338 kcal/100g", "C, K", "Copper, magnesium", "Fiber-rich, sleep aid", "Eating, smoothies, cereals", "Evening snack"),
    ("Tahini", "565 kcal", "17.7g", "26.7g", "0.3g", "48g", "11.8g", "5%", "565 kcal/100g", "B1, B2", "Copper, calcium", "Sesame paste, calcium-rich", "Hummus, dressings, baking", "Anytime"),
    ("Peanut Butter", "588 kcal", "25.8g", "20.5g", "7.7g", "50.4g", "6g", "1%", "588 kcal/100g", "B5, B7", "Copper, magnesium", "Protein-rich, energy boost", "Spreads, dressings, baking", "Breakfast or snack"),
    ("Almond Butter", "614 kcal", "21.6g", "20.4g", "4.4g", "54.1g", "3.5g", "1%", "614 kcal/100g", "B7, E", "Manganese, magnesium", "High protein, nutrient-dense", "Spreads, dressings, smoothies", "Breakfast or snack"),
    ("Cashew Butter", "587 kcal", "17.6g", "27.2g", "4.7g", "50.4g", "2.4g", "1%", "587 kcal/100g", "B5, B1", "Copper, magnesium", "Creamy, mineral-rich", "Spreads, dressings, smoothies", "Breakfast or snack"),
    ("Sunflower Seed Butter", "586 kcal", "17.3g", "20.3g", "1.8g", "52g", "4.5g", "1%", "586 kcal/100g", "B5, E", "Copper, selenium", "Allergen-free, nutrient-dense", "Spreads, dressings, smoothies", "Breakfast or snack"),
    ("Trail Mix", "464 kcal", "12.6g", "52.3g", "30.2g", "20.9g", "4.3g", "5%", "464 kcal/100g", "B5, E", "Copper, magnesium", "Mixed nuts, convenience", "Snacking, hiking, cereals", "Afternoon snack"),
    ("Mixed Nuts", "628 kcal", "18.7g", "21.6g", "4.7g", "58.6g", "6.8g", "3%", "628 kcal/100g", "B7, E", "Copper, magnesium", "Variety, mineral-rich", "Snacking, baking, salads", "Afternoon snack"),
    ("Energy Balls", "446 kcal", "9.2g", "60.1g", "48g", "18.7g", "3.4g", "7%", "446 kcal/100g", "B5, B9", "Copper, manganese", "Homemade snack, energy", "Eating, snacking, dessert", "Afternoon snack"),
    ("Granola", "471 kcal", "10.7g", "67.5g", "22g", "16.5g", "7.4g", "3%", "471 kcal/100g", "B5, B7", "Iron, magnesium", "Breakfast cereal, high fiber", "Cereal, yogurt, snacking", "Breakfast"),
    ("Granola Bars", "398 kcal", "7.3g", "59.2g", "28.4g", "13.8g", "2.9g", "6%", "398 kcal/100g", "B5, B7", "Iron, magnesium", "Convenient snack, energy", "Snacking, hiking, breakfast", "Breakfast or snack"),
    ("Energy Bars", "382 kcal", "8.4g", "56.2g", "24g", "12.1g", "3.1g", "8%", "382 kcal/100g", "B5, B9", "Iron, magnesium", "Nutrient-dense, convenient", "Snacking, pre-workout", "Breakfast or pre-workout"),
    ("Protein Bars", "346 kcal", "21.2g", "30.1g", "12g", "16.8g", "2.1g", "5%", "346 kcal/100g", "B5, B7", "Iron, magnesium", "High protein, muscle build", "Snacking, post-workout", "Post-workout"),
    ("Date Paste", "282 kcal", "2.7g", "75g", "66.5g", "0.4g", "6.7g", "21%", "282 kcal/100g", "B9, B6", "Copper, magnesium", "Natural sweetener, energy", "Sweetener, baking, cooking", "Anytime"),
    ("Nut Paste", "614 kcal", "21.6g", "20.4g", "4.4g", "54.1g", "3.5g", "1%", "614 kcal/100g", "B7, E", "Manganese, magnesium", "Homemade butter, nutrient-dense", "Spreads, dressings, smoothies", "Breakfast or snack"),
    ("Fruit Leather", "296 kcal", "2.1g", "74.7g", "57g", "0.4g", "1.2g", "17%", "296 kcal/100g", "C, A", "Copper, potassium", "Chewy snack, portable", "Snacking, lunch, hiking", "Afternoon snack"),
    ("Fruit Bars", "308 kcal", "3.2g", "76.5g", "61g", "1.1g", "2.3g", "15%", "308 kcal/100g", "C, A", "Copper, iron", "Portable snack, fruit-based", "Snacking, breakfast, hiking", "Afternoon snack"),
    ("Dried Multigrain", "364 kcal", "13.7g", "69.2g", "8.4g", "4.5g", "8.3g", "9%", "364 kcal/100g", "B1, B5", "Iron, manganese", "Whole grains, fiber-rich", "Cereals, baking, cooking", "Breakfast"),
    ("Muesli", "363 kcal", "8.6g", "72.8g", "19.1g", "6.5g", "6.8g", "5%", "363 kcal/100g", "B1, B5", "Iron, magnesium", "Breakfast cereal, fiber-rich", "Cereal, yogurt, breakfast", "Breakfast"),
    ("Dried Coconut Chips", "660 kcal", "7.3g", "24.2g", "9g", "64.5g", "9g", "3%", "660 kcal/100g", "B9, B5", "Manganese, copper", "Crunchy coconut, energy", "Eating, baking, cereals", "Afternoon snack"),
    ("Coconut Flakes", "660 kcal", "7.3g", "24.2g", "9g", "64.5g", "9g", "3%", "660 kcal/100g", "B9, B5", "Manganese, copper", "Sweet coconut, versatile", "Baking, cereals, smoothies", "Anytime"),
    ("Dried Mulberry", "305 kcal", "4.6g", "75g", "63g", "1.8g", "9.8g", "14%", "305 kcal/100g", "B9, C", "Iron, copper", "Iron-rich, sweet treat", "Eating, smoothies, baking", "Anytime snack"),
    ("Watermelon Seeds", "557 kcal", "28.3g", "15.3g", "2g", "47.7g", "1.5g", "5%", "557 kcal/100g", "B5, B9", "Copper, iron", "High protein, mineral-rich", "Raw eating, roasted, baking", "Afternoon snack"),
    ("Melon Seeds", "556 kcal", "28.4g", "11.2g", "1g", "47.6g", "2.8g", "5%", "556 kcal/100g", "B5, B9", "Copper, magnesium", "Mineral-rich, energy", "Raw eating, roasted, baking", "Afternoon snack"),
    ("Nigella Seeds", "375 kcal", "16.4g", "35g", "3g", "14.8g", "2.4g", "4%", "375 kcal/100g", "B1, B5", "Iron, copper", "Black cumin, antioxidant", "Spice, baking, cooking", "Anytime"),
    ("Caraway Seeds", "333 kcal", "19.8g", "49.9g", "0g", "14.6g", "38g", "9%", "333 kcal/100g", "B1, B5", "Iron, manganese", "Digestion aid, flavor", "Spice, baking, beverages", "With meals"),
    ("Fennel Seeds", "345 kcal", "15.8g", "52.3g", "0g", "14.8g", "39.8g", "9%", "345 kcal/100g", "B1, B5", "Iron, manganese", "Digestion aid, sweet", "Spice, teas, cooking", "After meals"),
    ("Dill Seeds", "305 kcal", "19.9g", "55.2g", "0g", "14.5g", "21.1g", "9%", "305 kcal/100g", "B1, B5", "Iron, manganese", "Digestion aid, pickling", "Spice, pickling, beverages", "With meals"),
    ("Poppy Seeds", "525 kcal", "17.9g", "28.1g", "1.7g", "41.6g", "8.6g", "5%", "525 kcal/100g", "B1, B5", "Copper, manganese", "High fat, baking", "Baking, paste, oil", "Anytime"),
    ("Mustard Seeds", "508 kcal", "26.1g", "28.1g", "6.4g", "36.2g", "6.3g", "5%", "508 kcal/100g", "B1, B5", "Copper, iron", "Spice, mineral-rich", "Spice, condiments, cooking", "Anytime"),
    ("Cumin Seeds", "375 kcal", "17.8g", "54.9g", "2.5g", "8.9g", "10.5g", "8%", "375 kcal/100g", "B1, B5", "Iron, manganese", "Digestion aid, spice", "Spice, cooking, curries", "With meals"),
    ("Coriander Seeds", "298 kcal", "12.4g", "54.9g", "1g", "17.8g", "41.9g", "9%", "298 kcal/100g", "K, B9", "Iron, manganese", "Digestion aid, anti-inflammatory", "Spice, chutney, cooking", "With meals"),
    ("Fenugreek Seeds", "323 kcal", "23.1g", "58.4g", "0.8g", "6.4g", "24.6g", "10%", "323 kcal/100g", "B9, B5", "Iron, magnesium", "Blood sugar control, spice", "Spice, tea, sprouting", "With meals"),
    ("Amchur Powder", "322 kcal", "3.3g", "80g", "71g", "0.2g", "1.6g", "15%", "322 kcal/100g", "A, C", "Copper, potassium", "Dried mango, tangy spice", "Spice, chutney, cooking", "With meals"),
    ("Dried Pomegranate", "249 kcal", "1.7g", "61.9g", "40.2g", "0.9g", "4.7g", "27%", "249 kcal/100g", "Vitamin C", "Copper, potassium", "Tart flavor, antioxidant", "Eating, snacking, baking", "Anytime snack"),
    ("Dried Guava", "285 kcal", "2.8g", "71.2g", "59g", "0.8g", "6.3g", "20%", "285 kcal/100g", "Vitamin C, A", "Copper, potassium", "Vitamin C rich, fiber", "Eating, baking, smoothies", "Afternoon snack"),
    ("Dried Passion Fruit", "271 kcal", "2.8g", "67.4g", "43g", "0.4g", "10.2g", "28%", "271 kcal/100g", "Vitamin C", "Iron, magnesium", "Fiber-rich, tropical", "Eating, beverages, baking", "Afternoon snack"),
    ("Dried Pumpkin", "304 kcal", "4.1g", "76g", "59g", "0.2g", "3.4g", "17%", "304 kcal/100g", "A, C", "Iron, manganese", "Beta-carotene, antioxidant", "Eating, baking, pies", "Afternoon snack"),
    ("Dried Cherry", "333 kcal", "1.6g", "85.5g", "65g", "0.2g", "1.6g", "10%", "333 kcal/100g", "Vitamin C", "Copper, manganese", "Sleep aid, antioxidant", "Eating, baking, cereals", "Evening snack"),
    ("Dried Raspberry", "353 kcal", "6.5g", "74g", "30g", "2.5g", "29.8g", "7%", "353 kcal/100g", "Vitamin C", "Copper, iron", "Fiber-rich, antioxidant", "Eating, baking, teas", "Anytime snack"),
    ("Dried Blackberry", "303 kcal", "4.9g", "76.4g", "32g", "1.6g", "13.4g", "14%", "303 kcal/100g", "Vitamin C", "Copper, iron", "Antioxidant, fiber-rich", "Eating, baking, teas", "Anytime snack"),
    ("Dried Goji Berry", "349 kcal", "14.3g", "77.1g", "48.3g", "1.5g", "13g", "6%", "349 kcal/100g", "A, C, B9", "Iron, copper", "Superfood, antioxidant", "Eating, smoothies, teas", "Morning or afternoon"),
    ("Dried Persimmon", "274 kcal", "1.5g", "73.5g", "70.3g", "0.2g", "1.6g", "15%", "274 kcal/100g", "A, C", "Copper, potassium", "Sweet treat, eye health", "Eating, baking, desserts", "Afternoon snack"),
    ("Dried Rambutan", "272 kcal", "3.7g", "67.9g", "60.9g", "1g", "1.5g", "27%", "272 kcal/100g", "Vitamin C", "Copper, magnesium", "Exotic fruit, immune", "Eating, smoothies, snacking", "Afternoon snack"),
    ("Dried Longan", "286 kcal", "3.5g", "72.4g", "63g", "0.2g", "1g", "12%", "286 kcal/100g", "Vitamin C", "Copper, iron", "Dragon's eye, energy", "Eating, smoothies, teas", "Afternoon snack"),
    ("Dried Jujube", "322 kcal", "3.7g", "81.8g", "63.5g", "0.2g", "1.5g", "14%", "322 kcal/100g", "B9, B5", "Copper, iron", "Sleep aid, immune boost", "Eating, teas, soups", "Evening snack"),
    ("Dried Wolfberry", "349 kcal", "14.3g", "77.1g", "48.3g", "1.5g", "13g", "6%", "349 kcal/100g", "A, C", "Iron, copper", "Superfood alternative", "Smoothies, teas, cereals", "Morning breakfast"),
]

def seed_database():

    if Food.query.count() > 0:
        return

    all_food_data = []

    for name, cal, prot, carbs, sug, fat, fiber, water, energy, vit, min, ben, uses, when in fruits_list:
        all_food_data.append(Food(name=name, category='Fruit', calories=cal, protein=prot, carbs=carbs, sugars=sug, fat=fat, fiber=fiber, water=water, energy=energy, vitamins=vit, minerals=min, benefits=ben, uses=uses, when_to_eat=when))

    for name, cal, prot, carbs, sug, fat, fiber, water, energy, vit, min, ben, uses, when in vegetables_list:
        all_food_data.append(Food(name=name, category='Vegetable', calories=cal, protein=prot, carbs=carbs, sugars=sug, fat=fat, fiber=fiber, water=water, energy=energy, vitamins=vit, minerals=min, benefits=ben, uses=uses, when_to_eat=when))

    for name, cal, prot, carbs, sug, fat, fiber, water, energy, vit, min, ben, uses, when in dryfruits_list:
        all_food_data.append(Food(name=name, category='Dry Fruit', calories=cal, protein=prot, carbs=carbs, sugars=sug, fat=fat, fiber=fiber, water=water, energy=energy, vitamins=vit, minerals=min, benefits=ben, uses=uses, when_to_eat=when))

    db.session.bulk_save_objects(all_food_data)
    db.session.commit()


with app.app_context():
    db.create_all()
    seed_database()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/search", methods=["POST"])
def search():

    data = request.get_json()

    food_name = data.get("food", "").strip()

    if not food_name:
        return jsonify({
            "error": "Please enter a food name"
        }), 400

    time.sleep(2)

    food = Food.query.filter(
        Food.name.ilike(f"%{food_name}%")
    ).first()

    if not food:
        return jsonify({
            "error": "Food not found"
        }), 404

    return jsonify({
        "name": food.name,
        "category": food.category,
        "calories": food.calories,
        "protein": food.protein,
        "carbs": food.carbs,
        "sugars": food.sugars,
        "fat": food.fat,
        "fiber": food.fiber,
        "vitamins": food.vitamins,
        "minerals": food.minerals,
        "water": food.water,
        "energy": food.energy,
        "benefits": food.benefits,
        "uses": food.uses,
        "when_to_eat": food.when_to_eat
    })


@socketio.on("search_food")
def handle_search(data):

    socketio.emit(
        "search_notification",
        {
            "message":
            f"{data.get('food')} searched"
        }
    )


if __name__ == "__main__":

    socketio.run(
        app,
        host="0.0.0.0",
        port=5000,
        debug=True
    )
