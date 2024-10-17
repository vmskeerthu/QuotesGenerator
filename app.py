from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
import random

app = Flask(__name__)

# MongoDB connection
client = MongoClient("mongodb+srv://mkeerthu2906:zkAkUsEhq2dgqZKo@cluster0.teui3.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")  # Update this if using MongoDB Atlas
db = client['quote_db']  # Database name
quotes_collection = db['quotes']  # Collection name

@app.route('/')
def home():
    # Fetch a random quote from MongoDB
    quotes = list(quotes_collection.find())
    random_quote = random.choice(quotes) if quotes else {"text": "No quotes found.", "author": "Unknown"}
    return render_template('index.html', quote=random_quote)

@app.route('/add', methods=['GET', 'POST'])
def add_quote():
    if request.method == 'POST':
        # Get form data
        text = request.form['quote']
        author = request.form['author']
        
        # Save to MongoDB
        if text and author:
            quotes_collection.insert_one({"text": text, "author": author})
        return redirect(url_for('home'))

    return render_template('add_quote.html')

if __name__ == '__main__':
    app.run(debug=True)
