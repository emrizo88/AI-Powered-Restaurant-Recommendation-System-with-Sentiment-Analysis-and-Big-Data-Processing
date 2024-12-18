import json
import pandas as pd

# Load the business.json file
restaurant_ids = set()  # To store business_ids of restaurants

with open('D:\Profesional\IRS_Semestres\IRS_Semestre_7\Intro_BigData\Dataset\yelp_academic_dataset_business.json', 'r', encoding='utf-8') as business_file:
    for line in business_file:
        business = json.loads(line)
        if 'categories' in business and business['categories']:
            categories = business['categories'].lower()
            # Check if the business is a restaurant based on categories
            if 'restaurant' in categories:
                restaurant_ids.add(business['business_id'])

# Now, filter the reviews.json based on restaurant business_ids
with open('D:\Profesional\IRS_Semestres\IRS_Semestre_7\Intro_BigData\Dataset\yelp_academic_dataset_review.json', 'r', encoding='utf-8') as review_file, \
        open('filtered_reviews.json', 'w', encoding='utf-8') as output_file:
    for line in review_file:
        review = json.loads(line)
        if review['business_id'] in restaurant_ids:
            json.dump(review, output_file)
            output_file.write('\n')  # Add new line after each review
