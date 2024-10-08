from tasks import fetch_and_store_articles, classify_and_update_articles

# Trigger the tasks
fetch_and_store_articles.delay()  # Fetch and store articles in the database
classify_and_update_articles.delay()  # Classify the stored articles
