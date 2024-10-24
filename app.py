from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient
from bson.objectid import ObjectId
import random

app = Flask(__name__)
import secrets
app.secret_key = secrets.token_hex(16) 


client = MongoClient("mongodb+srv://mkeerthu2906:zkAkUsEhq2dgqZKo@cluster0.teui3.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")  
db = client['quote_db']  
quotes_collection = db['quotes']  


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/random')
def random_quote():
    quotes = list(quotes_collection.find())
    random_quote = random.choice(quotes) if quotes else {"text": "No quotes found.", "author": "Unknown"}
    return render_template('random_quote.html', quote=random_quote)

@app.route('/random/refresh')
def refresh_random_quote():
    return redirect(url_for('random_quote'))


@app.route('/add', methods=['GET', 'POST'])
def add_quote():
    if request.method == 'POST':
        text = request.form['quote']
        author = request.form['author']
        if text and author:
            quotes_collection.insert_one({"text": text, "author": author})
            flash("Quote added successfully!")
        return redirect(url_for('view_all'))
    return render_template('add_quote.html')

@app.route('/view_all')
def view_all():
    quotes = list(quotes_collection.find())
    return render_template('view_all.html', quotes=quotes)

@app.route('/edit/<quote_id>', methods=['GET', 'POST'])
def edit_quote(quote_id):
    quote = quotes_collection.find_one({"_id": ObjectId(quote_id)})
    if request.method == 'POST':
        new_text = request.form['quote']
        new_author = request.form['author']
        quotes_collection.update_one({"_id": ObjectId(quote_id)}, {"$set": {"text": new_text, "author": new_author}})
        flash("Quote updated successfully!")
        return redirect(url_for('view_all'))
    return render_template('edit_quote.html', quote=quote)

@app.route('/delete/<quote_id>', methods=['POST'])
def delete_quote(quote_id):
    quotes_collection.delete_one({"_id": ObjectId(quote_id)})
    flash("Quote deleted successfully!")
    return redirect(url_for('view_all'))
@app.route('/toggle_favorite/<quote_id>', methods=['POST'])
def toggle_favorite(quote_id):
    quote = quotes_collection.find_one({"_id": ObjectId(quote_id)})
    if quote:
        new_favorite_status = not quote.get('favorite', False)  # Toggle the favorite status
        quotes_collection.update_one({"_id": ObjectId(quote_id)}, {"$set": {"favorite": new_favorite_status}})
        flash("Favorite status updated successfully!")
    return redirect(url_for('view_all'))


@app.route('/favorite/<quote_id>', methods=['POST'])
def favorite_quote(quote_id):
    quote = quotes_collection.find_one({"_id": ObjectId(quote_id)})
    if quote:
        new_favorite_status = not quote.get('favorite', False)
        quotes_collection.update_one({"_id": ObjectId(quote_id)}, {"$set": {"favorite": new_favorite_status}})
        flash("Quote favorite status updated!")
    return redirect(url_for('view_all'))

@app.route('/favorites')
def view_favorites():
    favorite_quotes = list(quotes_collection.find({"favorite": True}))
    return render_template('favorites.html', quotes=favorite_quotes)

@app.route('/search', methods=['GET', 'POST'])
def search_quotes():
    if request.method == 'POST':
        search_term = request.form['search']
        quotes = list(quotes_collection.find({"$or": [{"text": {"$regex": search_term, "$options": "i"}}, {"author": {"$regex": search_term, "$options": "i"}}]}))
        if quotes:
            return render_template('search_results.html', quotes=quotes)
        else:
            flash("No results found!")
            return redirect(url_for('search_quotes'))
    return render_template('search.html')

if __name__ == '__main__':
    app.run(debug=True)
