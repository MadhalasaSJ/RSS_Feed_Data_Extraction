# RSS Feed Extraction and Classification

## Overview

This application fetches articles from various RSS feeds, classifies the content into predefined categories, and stores the results in a SQLite database. It uses **Celery** for asynchronous processing, **SQLAlchemy** for database interactions, and **spaCy** for natural language processing (NLP) tasks.

## Components

### 1. RSS Feed Fetching

- **Libraries Used**: `feedparser`, `requests`
- **Functionality**:
  - The application fetches articles from a list of RSS feeds using the `feedparser` library. 
  - If a fetch request fails due to network issues or server errors, a retry mechanism is implemented using the `requests` library's `Retry` functionality.
  
- **Implementation**:
  - The `fetch_rss_with_retry` function handles fetching and parsing the RSS feeds.
  - Articles are extracted from the feed entries, and relevant data such as title, content, publication date, and source URL are stored.

### 2. Database Storage

- **Libraries Used**: `SQLAlchemy`
- **Functionality**:
  - Articles are stored in an SQLite database for persistent storage.
  - The database schema is defined using SQLAlchemy ORM, allowing for easy data manipulation and retrieval.

- **Implementation**:
  - The `Article` class defines the structure of the articles table with fields: `id`, `title`, `content`, `pub_date`, `source_url`, and `category`.
  - The `store_articles` function saves the fetched articles into the database.

### 3. Asynchronous Processing

- **Libraries Used**: `Celery`
- **Functionality**:
  - Celery is used to manage asynchronous tasks, allowing for non-blocking fetching and classification of articles.
  - Redis serves as the message broker to facilitate communication between the worker and the main application.

- **Implementation**:
  - Two main Celery tasks are defined: `fetch_and_store_articles` for fetching articles and `classify_and_update_articles` for classifying them.
  - Each task runs independently, and results are stored back in the database.

### 4. Article Classification

- **Libraries Used**: `spaCy`, `nltk`
- **Functionality**:
  - Articles are classified into predefined categories: 
    - **Terrorism / protest / political unrest / riot**
    - **Positive/Uplifting**
    - **Natural Disasters**
    - **Others**
  - A list of keywords and synonyms is used to match article content to the categories.

- **Implementation**:
  - The `classify_article` function uses `spaCy` to process the content and checks for the presence of keywords (including synonyms obtained from WordNet using `nltk`).
  - Articles that do not match any category keywords are classified as "Others".

### 5. Data Export

- **Functionality**:
  - The application provides functionality to export the articles in three formats: SQL dump, CSV, and JSON.
  
- **Implementation**:
  - **SQL Dump**: Created using SQLite commands to capture the schema and data of the articles table.
  - **JSON**: A separate Python script fetches articles from the database and converts them to JSON format for easy consumption.

## Design Choices

1. **Asynchronous Processing with Celery**: 
   - Asynchronous task management allows the application to fetch and classify articles concurrently, improving efficiency and responsiveness.

2. **Use of SQLAlchemy for ORM**: 
   - SQLAlchemy simplifies database interactions and abstracts away the underlying SQL syntax, making the code cleaner and easier to maintain.

3. **Keyword Matching for Classification**: 
   - Utilizing a combination of keywords and synonyms allows for broader coverage of potential matching terms, improving the accuracy of article classification.

4. **Error Handling**:
   - The application includes robust error handling for network requests and database operations, ensuring that the system remains stable and provides useful error messages.

5. **Data Export Options**:
   - Providing multiple formats for data export enhances the flexibility of the application, allowing users to choose the format that best suits their needs.

## Setup Instructions

1. **Prerequisites**:
   - Python 3.x installed
   - Redis server running

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt

3. **Download NLTK Data**:
   ```bash
   python -m nltk.downloader wordnet

4. **Start Redis**:
   - Make sure the Redis server is up and running.

5. **Run the Celery Worker**:
   ```bash
   celery -A tasks worker --loglevel=info

6. **Run the Main Script**:
   ```bash
   python main.py

7. **Export Data**:
   - To export articles to SQL and get the data in JSON formats, run the appropriate export script.
   ```bash
   python database.py            
