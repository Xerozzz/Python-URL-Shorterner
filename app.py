import sqlite3
from hashids import Hashids
from flask import Flask, render_template, request, flash, redirect, url_for


def connect_db():  # Connection to DB
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'  # TO BE EDITED, MININUM 4 CHARACTERS
hashids = Hashids(min_length=4, salt=app.config['SECRET_KEY'])


@app.route('/', methods=('GET', 'POST'))  # Route to create URL + Home Page
def index():
    # Connect to DB
    conn = connect_db()
    # POST Method
    if request.method == 'POST':
        url = request.form['url']

        # Makes sure URL exists
        if not url:
            flash("A URL IS REQUIRED!!!")
            return redirect(url_for('index'))

        # Inserts URL into DB
        url_data = conn.execute(
            'INSERT INTO urls (original_url) VALUES (?)', (url,))

        conn.commit()
        conn.close()

        # Generates Hash ID and short url
        url_id = url_data.lastrowid
        hashid = hashids.encode(url_id)
        short_url = request.host_url + hashid

        return render_template('index.html', short_url=short_url)
    return render_template('index.html')


@app.route('/<id>')  # Route to redirect to original URL
def url_redirect(id):
    conn = connect_db()

    original_id = hashids.decode(id)
    if original_id:
        original_id = original_id[0]
        url_data = conn.execute('SELECT original_url, clicks FROM urls'
                                ' WHERE id = (?)', (original_id,)
                                ).fetchone()
        original_url = url_data['original_url']
        clicks = url_data['clicks']

        conn.execute('UPDATE urls SET clicks = ? WHERE id = ?',
                     (clicks+1, original_id))

        conn.commit()
        conn.close()
        return redirect(original_url)
    else:
        flash('Invalid URL')
        return redirect(url_for('index'))


@app.route('/stats', methods=('GET', 'POST'))    # Route to statistics page
def stats():
    # Post Request
    if request.method == 'POST':
        print(request)

    # Get Request
    if request.method == 'GET':
        conn = connect_db()
        db_urls = conn.execute('SELECT id, created, original_url, clicks FROM urls'
                               ).fetchall()
        conn.close()
        urls = []
        for url in db_urls:
            url = dict(url)
            url['short_url'] = request.host_url + hashids.encode(url['id'])
            urls.append(url)
        return render_template('stats.html', urls=urls)
