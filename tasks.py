import logging
import feedparser
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
from celery import Celery
import spacy
from nltk.corpus import wordnet

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize Celery
app = Celery('tasks', broker='redis://localhost:6379/0')

# Set up the database
DATABASE_URL = "sqlite:///articles14.db"
engine = create_engine(DATABASE_URL)
Base = declarative_base()

class Article(Base):
    __tablename__ = 'articles14'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    content = Column(String)
    pub_date = Column(DateTime)
    source_url = Column(String)
    category = Column(String)

# Create the database table
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# Retry settings for failed requests
retry_strategy = Retry(
    total=3,  # Number of retries
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "OPTIONS"],
    backoff_factor=1  # Wait time between retries
)

adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("https://", adapter)
http.mount("http://", adapter)

# Custom fetch function with retry logic and SSL verification disabled
def fetch_rss_with_retry(url):
    try:
        response = http.get(url, verify=False) 
        return feedparser.parse(response.content)
    except Exception as e:
        logging.error(f"Failed to fetch {url}: {e}")
        return None

# RSS Feeds
rss_feeds = [
    "https://edition.cnn.com/services/rss/rss.cnn_topstories.rss",
    "https://feeds.bbci.co.uk/news/world/asia/india/rss.xml",
    "https://www.reuters.com/rssFeed/businessNews",
    "https://qz.com/feed",
    "https://feeds.foxnews.com/foxnews/politics",
    "https://feeds.feedburner.com/NewshourWorld",
]

# Function to get synonyms for keywords
def get_synonyms(word):
    synonyms = set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name())  
    return synonyms

# Define categories with keywords and synonyms
categories = {
    "Terrorism / protest / political unrest / riot": [
        "terrorism", "protest", "riot", "political", "unrest", "violence", "militant", "demonstration", "uprising", "rebellion",
        *get_synonyms("terrorism"),
        *get_synonyms("protest"),
        *get_synonyms("violence"),
        *get_synonyms("riot"),
        *get_synonyms("conflict")
    ],
    "Positive/Uplifting": [
        "happy", "inspiring", "positive", "success", "achievement", "growth", "celebration", "good news", "motivation",
        *get_synonyms("happy"),
        *get_synonyms("positive"),
        *get_synonyms("success"),
        *get_synonyms("celebrate")
    ],
    "Natural Disasters": [
        "earthquake", "flood", "hurricane", "wildfire", "tsunami", "storm", "disaster", "tornado", "cyclone", "drought",
        *get_synonyms("earthquake"),
        *get_synonyms("flood"),
        *get_synonyms("disaster"),
        *get_synonyms("storm")
    ]
}

# Task to fetch articles
@app.task
def fetch_and_store_articles():
    articles = []
    for feed in rss_feeds:
        parsed_feed = fetch_rss_with_retry(feed)
        if parsed_feed:
            for entry in parsed_feed.entries:
                content = entry.get('summary', entry.get('description', ''))
                article = {
                    'title': entry.title,
                    'content': content,
                    'pub_date': datetime.now(),
                    'source_url': entry.link
                }
                articles.append(article)
    store_articles(articles)

# Function to store articles in the database
def store_articles(articles):
    for article in articles:
        new_article = Article(
            title=article['title'],
            content=article['content'],
            pub_date=article['pub_date'],
            source_url=article['source_url'],
            category=None  # Category will be set after classification
        )
        session.add(new_article)
    session.commit()
    logging.info(f"Stored {len(articles)} articles.")

# Load spaCy model
nlp = spacy.load("en_core_web_md")  

# Improved classification function with enhanced keyword matching
def classify_article(content):
    doc_text = content.lower()  # Convert content to lowercase for case-insensitive matching
    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword in doc_text:  # Check if keyword exists in the article content
                return category
    return "Others"

# Task to classify articles
@app.task
def classify_and_update_articles():
    articles = session.query(Article).filter(Article.category == None).all()
    for article in articles:
        article.category = classify_article(article.content)
    session.commit()
    logging.info(f"Classified {len(articles)} articles.")

# Main function to trigger the fetching and classification
def main():
    # Trigger fetching and storing of articles
    fetch_and_store_articles.delay()
    # Trigger classification of articles
    classify_and_update_articles.delay()

if __name__ == "__main__":
    main()
