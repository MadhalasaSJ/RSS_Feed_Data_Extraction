import sqlite3
import json

try:
    # Connect to the SQLite database
    conn = sqlite3.connect('articles14.db')  # Adjust the path if necessary
    cursor = conn.cursor()

    # Execute a query to fetch all articles from the 'articles' table
    cursor.execute("SELECT * FROM articles14")  # Change this to your correct table name

    # Fetch all rows from the executed query
    rows = cursor.fetchall()

    # Convert the rows into a list of dictionaries
    articles_list = []
    for row in rows:
        articles_list.append({
            'ID': row[0],
            'Title': row[1],
            'Content': row[2],
            'Pub Date': row[3],
            'Source URL': row[4],
            'Category': row[5]
        })

    # Export the articles to a JSON file
    with open('articles.json', 'w') as json_file:
        json.dump(articles_list, json_file, indent=4)  # Indent for pretty printing

    print("Exported articles to articles.json")

except sqlite3.Error as e:
    print(f"An error occurred: {e}")

finally:
    # Close the connection
    if conn:
        conn.close()
