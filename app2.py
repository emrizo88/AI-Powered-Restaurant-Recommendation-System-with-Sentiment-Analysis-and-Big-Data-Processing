from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import numpy as np
import random
import json
import os
from math import radians, sin, cos, sqrt, atan2
from waitress import serve

app = Flask(__name__)

# File paths
CSV_FILE_PATH = 'D:\Profesional\IRS_Semestres\IRS_Semestre_7\Intro_BigData\philadelphia_restaurants_with_distance2.csv'
PREFERENCE_FILE = 'D:\Profesional\IRS_Semestres\IRS_Semestre_7\Intro_BigData\preference_matrix.json'

# List of survey questions for frontend
questions = [
    "How essential is it for you to have options for family-style dining or sharing plates?",
    "How much do you appreciate themed dining experiences that enhance the food enjoyment?",
    "How significant is it for you to find places with special events centered around food?",
    "How essential is it for you to know about the signature dishes or specialties of a restaurant?",
    "How important is it for you to find restaurants that specialize in specific culinary techniques?",
    "How important is it for you to have dishes that are highly recommended by other customers?",
    "How essential is it for you to know about the average wait time for food once ordered?",
    "How important is it for you to have a restaurant that emphasizes a comfortable and inviting atmosphere?",
    "How significant is it for you to find restaurants that offer a variety of cuisines to choose from?",
    "How essential is it for you to see dietary options (e.g., vegan, gluten-free) clearly listed on the menu?",
    "How important is it for you to find places that offer tasting menus or chef’s specials?",
    "How significant is it for you to find places that are known for quick service or fast casual dining options?",
]

# Function to calculate Haversine distance
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in kilometers
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

# Update CSV with new distances based on user location
def update_distances_in_csv(user_lat, user_lon):
    df = pd.read_csv(CSV_FILE_PATH)
    df['distance_km'] = df.apply(lambda row: haversine(user_lat, user_lon, row['latitude'], row['longitude']), axis=1)
    df.to_csv(CSV_FILE_PATH, index=False)

# Update and weight preferences
def update_and_weight_preferences(preference_matrix, new_preferences):
    updated_matrix = [[0.5 * pref for pref in row] for row in preference_matrix]
    updated_matrix.append(new_preferences)
    return updated_matrix

# Save and load preferences
def save_preferences(preference_matrix):
    with open(PREFERENCE_FILE, 'w') as f:
        json.dump(preference_matrix, f)

def load_preferences():
    if os.path.exists(PREFERENCE_FILE):
        with open(PREFERENCE_FILE, 'r') as f:
            return json.load(f)
    return []

# Calculate weighted preferences
def calculate_weighted_preferences(preference_matrix):
    validated_matrix = [row for row in preference_matrix if len(row) == 22]
    return np.sum(validated_matrix, axis=0) if validated_matrix else [0] * 22

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        distance_question = int(request.form.get('distance_quest', 0))
        
        # Create a binary list for selected cuisines
        feature_options_count = 9
        selected_features = [0] * feature_options_count
        selected_feature_indices = [int(f) - 1 for f in request.form.getlist('features')]
        for idx in selected_feature_indices:
            selected_features[idx] = 1

        location_lat = float(request.form.get('latitude'))
        location_lng = float(request.form.get('longitude'))
        survey_answers = [int(request.form.get(f'q{i}', 0)) for i in range(12)]
        final_result = [distance_question] + survey_answers + selected_features

        update_distances_in_csv(location_lat, location_lng)

        preference_matrix = load_preferences()
        preference_matrix = update_and_weight_preferences(preference_matrix, final_result)
        save_preferences(preference_matrix)

        return redirect(url_for('return_recommendation'))

    selected_questions = random.sample(list(enumerate(questions)), 5)
    return render_template('feedback.html', questions=selected_questions)

@app.route('/return_recommendation')
def return_recommendation():
    df = pd.read_csv(CSV_FILE_PATH)
    preference_matrix = load_preferences()
    weighted_preferences = calculate_weighted_preferences(preference_matrix)

        # Calculate scores based on weighted preferences
    def calculate_score(row):
        distance_score = 1 / (row['distance_km'] + 1)
        review_score = row.get('Normalized_Score', 0)
        
        # Check if 'attributes' and 'categories' are not NaN before checking for keywords
        family_style_score = 1 if isinstance(row['attributes'], str) and 'family-style' in row['attributes'] else 0
        experience_score = 1 if isinstance(row['attributes'], str) and any(keyword in row['attributes'] for keyword in ["themed dining", "ambience", "decor", "experience", "atmosphere"]) else 0
        special_score = 1 if isinstance(row['attributes'], str) and any(keyword in row['attributes'] for keyword in ["events", "wine tasting", "food festivals", "special events", "event spaces"]) else 0
        specialties_score = 1 if isinstance(row['attributes'], str) and any(keyword in row['attributes'] for keyword in ["signature dish", "specialty", "chef's special", "top dishes", "recommended dishes"]) else 0
        culinary_score = 1 if isinstance(row['attributes'], str) and any(keyword in row['attributes'] for keyword in ["wood-fired", "sous-vide", "grilled", "cooking techniques", "unique preparation"]) else 0
        popular_score = 1 if isinstance(row['attributes'], str) and any(keyword in row['attributes'] for keyword in ["popular dishes", "highly rated", "recommended by customers", "top-rated dishes"]) else 0
        wait_score = 1 if isinstance(row['attributes'], str) and any(keyword in row['attributes'] for keyword in ["wait time", "order time", "speed of service", "service time"]) else 0
        comfy_score = 1 if isinstance(row['attributes'], str) and any(keyword in row['attributes'] for keyword in ["cozy", "comfortable", "inviting", "ambiance", "decor"]) else 0
        variety_score = 1 if isinstance(row['attributes'], str) and any(keyword in row['attributes'] for keyword in ["variety", "multiple cuisines", "diverse menu", "cuisine options"]) else 0
        diet_score = 1 if isinstance(row['attributes'], str) and any(keyword in row['attributes'] for keyword in ["dietary options", "vegan", "gluten-free", "menu labels", "allergy-friendly"]) else 0
        tasting_score = 1 if isinstance(row['attributes'], str) and any(keyword in row['attributes'] for keyword in ["tasting menu", "chef’s special", "prix fixe", "sampler"]) else 0
        quick_score = 1 if isinstance(row['attributes'], str) and any(keyword in row['attributes'] for keyword in ["quick service", "fast casual", "express", "speedy dining", "quick meals"]) else 0

        # Check for cuisine categories
        bakery_score = 1 if isinstance(row['categories'], str) and 'Bakeries' in row['categories'] else 0
        italian_food_score = 1 if isinstance(row['categories'], str) and 'Italian' in row['categories'] else 0
        mexican_food_score = 1 if isinstance(row['categories'], str) and 'Mexican' in row['categories'] else 0
        chinese_food_score = 1 if isinstance(row['categories'], str) and 'Chinese' in row['categories'] else 0
        indian_food_score = 1 if isinstance(row['categories'], str) and 'Indian' in row['categories'] else 0
        thai_food_score = 1 if isinstance(row['categories'], str) and 'Thai' in row['categories'] else 0
        japanese_food_score = 1 if isinstance(row['categories'], str) and 'Japanese' in row['categories'] else 0
        vegan_food_score = 1 if isinstance(row['categories'], str) and 'Vegan' in row['categories'] else 0

        # Calculate 'others' score if no specific cuisine matches
        others_score = 1 if not any([bakery_score, italian_food_score, mexican_food_score, chinese_food_score, indian_food_score, thai_food_score, japanese_food_score, vegan_food_score]) else 0

        # Calculate final score using the weighted preferences
        score = (weighted_preferences[0] * distance_score) + \
                (weighted_preferences[1] * family_style_score) + \
                (weighted_preferences[2] * experience_score) + \
                (weighted_preferences[3] * special_score) + \
                (weighted_preferences[4] * specialties_score) + \
                (weighted_preferences[5] * culinary_score) + \
                (weighted_preferences[6] * popular_score) + \
                (weighted_preferences[7] * wait_score) + \
                (weighted_preferences[8] * comfy_score) + \
                (weighted_preferences[9] * variety_score) + \
                (weighted_preferences[10] * diet_score) + \
                (weighted_preferences[11] * tasting_score) + \
                (weighted_preferences[12] * quick_score) + \
                (weighted_preferences[13] * bakery_score) + \
                (weighted_preferences[14] * italian_food_score) + \
                (weighted_preferences[15] * mexican_food_score) + \
                (weighted_preferences[16] * chinese_food_score) + \
                (weighted_preferences[17] * indian_food_score) + \
                (weighted_preferences[18] * thai_food_score) + \
                (weighted_preferences[19] * japanese_food_score) + \
                (weighted_preferences[20] * vegan_food_score) + \
                (weighted_preferences[21] * others_score) + \
                review_score
        return score


    df['score'] = df.apply(calculate_score, axis=1)
    max_score, min_score = df['score'].max(), df['score'].min()
    df['Final_score'] = 100 * (df['score'] - min_score) / (max_score - min_score)
    df_ranked = df.sort_values(by='Final_score', ascending=False)

    top_restaurants = df_ranked[['name', 'stars', 'distance_km', 'Final_score']].head(10).to_dict(orient='records')
    return render_template('return.html', recommendations=top_restaurants)

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=8080)
