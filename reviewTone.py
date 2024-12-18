import csv
from textblob import TextBlob

# Define the sentiment analysis function
def clasificar_review(review):
    # Analyze the sentiment of the review using TextBlob
    blob = TextBlob(review)
    # Sentiment score ranges from -1 (very negative) to 1 (very positive)
    sentimiento = blob.sentiment.polarity
    # Consider positive if sentiment > 0, negative otherwise
    return 1 if sentimiento > 0 else 0

# Function to read review text from a CSV file
def procesar_review_desde_csv(csv_filename, row_index=0):
    with open(csv_filename, 'r', encoding='utf-8') as csv_file:
        reader = csv.reader(csv_file)
        next(reader)  # Skip the header
        for idx, row in enumerate(reader):
            if idx == row_index:
                review_text = row[7]  # Assuming the review text is in the 8th column (index 7)
                print(f"Review: {review_text}")
                clasificacion = clasificar_review(review_text)
                return clasificacion

# Usage example
csv_filename = 'D:/Profesional/IRS_Semestres/IRS_Semestre_7/Intro_BigData/filtered_reviews_philadelphia.csv'
clasificacion = procesar_review_desde_csv(csv_filename, row_index=0)
print(f"Clasificación de la reseña: {clasificacion}")  # 1 (positive) or 0 (negative)
