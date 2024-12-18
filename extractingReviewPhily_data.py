import json
import csv

# Load the business.json file and collect restaurant business IDs for those in Philadelphia
restaurant_ids_in_philadelphia = set()

with open('D:\Profesional\IRS_Semestres\IRS_Semestre_7\Intro_BigData\Dataset\yelp_academic_dataset_business.json', 'r', encoding='utf-8') as business_file:
    for line in business_file:
        business = json.loads(line)
        if 'categories' in business and business['categories']:
            categories = business['categories'].lower()
            # Check if the business is a restaurant based on categories and is in Philadelphia
            if 'restaurant' in categories and business['city'].lower() == 'philadelphia':
                restaurant_ids_in_philadelphia.add(business['business_id'])

# Now, filter the review.json based on restaurant business_ids and save to CSV
with open('D:\Profesional\IRS_Semestres\IRS_Semestre_7\Intro_BigData\Dataset\yelp_academic_dataset_review.json', 'r', encoding='utf-8') as review_file, \
        open('filtered_reviews_philadelphia.csv', 'w', newline='', encoding='utf-8') as csv_file:

    # Define CSV columns (choose relevant fields from the reviews)
    csv_writer = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
    csv_writer.writerow(['review_id', 'user_id', 'business_id', 'stars', 'useful', 'funny', 'cool', 'text', 'date'])  # header

    # Filter and write reviews for restaurants in Philadelphia
    for line in review_file:
        review = json.loads(line)
        if review['business_id'] in restaurant_ids_in_philadelphia:
            # Write the review data to the CSV
            csv_writer.writerow([
                review['review_id'],
                review['user_id'],
                review['business_id'],
                review['stars'],
                review['useful'],
                review['funny'],
                review['cool'],
                review['text'].replace('\n', ' ').replace('\r', ' '),  # Replace newlines in the text
                review['date']
            ])
