import sqlite3
from hashids import Hashids
from flask import Flask, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash

# Connect to DB
def connect_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'  # TO BE EDITED, MININUM 4 CHARACTERS
hashids = Hashids(min_length=4, salt=app.config['SECRET_KEY'])

# Route to home/index page
@app.route('/', methods=('GET', 'POST'))  # Route to create URL + Home Page
def index():
    # Connect to DB
    conn = connect_db()
    # POST Method
    if request.method == 'POST':
        url = request.form['url']

        # Makes sure URL exists
        if not url:
            flash("A URL IS REQUIRED!")
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

# Route to route to original URL
@app.route('/<id>')
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

# Route for statistics page
@app.route('/stats', methods=('GET', 'POST'))    # Route to statistics page
def stats():
    # Post Request
    if request.method == 'POST':
        conn = connect_db()
        # print(request.form['rowId'])
        rowId = request.form['rowId']
        db_urls = conn.execute('DELETE from urls WHERE id = ?', rowId)
        conn.commit()
        conn.close()
        flash("Link Deleted!")

    # Get Request
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

# Route for login page and function
@app.route("/login", methods=('GET', 'POST'))
def login():
    return render_template('login.html')

# Route for signup page and function
@app.route("/signup", methods=('GET', 'POST'))
def signup():
    if request.method == 'POST':
        # Get sign up form data
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        # Check if email or username already exists
        try:
            conn = connect_db()
            conn.execute("INSERT into users (email, username, password) VALUES (?, ?, ?)",(email,username,password))
            conn.commit()
            conn.close()
        except sqlite3.Error as err:
            if "username" in str(err):
                flash("Username already used! Try another or login!")
            elif "email" in str(err):
                flash("Email already used! Try another or login!")
            else:
                flash("Oops. Something went wrong, please try again. If the issue persists, please contact support")
    conn = connect_db()
    data = conn.execute("SELECT * from users").fetchall()
    conn.close()
    return render_template('signup.html')
