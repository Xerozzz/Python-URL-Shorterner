import sqlite3
from hashids import Hashids
from flask import Flask, render_template, request, flash, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

# Connect to DB
def connect_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'  # TO BE EDITED, MININUM 4 CHARACTERS
hashids = Hashids(min_length=4, salt=app.config['SECRET_KEY'])
# Route to home/home page
@app.route('/home', methods=('GET', 'POST'))  # Route to create URL + Home Page
def home():
    try: 
        print(session['userid'])
        # POST Method
        if request.method == 'POST':
            # Connect to DB
            conn = connect_db()
            url = request.form['url']

            # Makes sure URL exists
            if not url:
                flash("A URL IS REQUIRED!")
                return redirect(url_for('home'))

            # Inserts URL into DB
            url_data = conn.execute(
                'INSERT INTO urls (original_url) VALUES (?)', (url,))
            conn.commit()
            conn.close()
            # Generates Hash ID and short url
            url_id = url_data.lastrowid
            hashid = hashids.encode(url_id)
            short_url = request.host_url + hashid

            return render_template('home.html', short_url=short_url, logged_in=True, username = session['username'])
        return render_template('home.html', logged_in=True, username = session['username'])
    except:
        flash("Please Log In!")
        return redirect(url_for('login'))

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
        return redirect(url_for('home'))

# Route for statistics page
@app.route('/stats', methods=('GET', 'POST'))    # Route to statistics page
def stats():
    try: 
        session['userid']
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
        return render_template('stats.html', urls=urls, logged_in=True)
    except:
        flash("Please Log In!")
        return redirect(url_for('login'))

# Route for login page and function
@app.route("/", methods=('GET', 'POST'))
def login():
    try: 
        session['userid']
        return redirect(url_for('home'))
    except:
        if request.method == 'POST':
            # Get sign up form data
            email = request.form.get('email')
            password = request.form.get('password')
            # Check if email or username already exists
            conn = connect_db()
            url_data = conn.execute("SELECT * from users where email = ?",(email,)).fetchone()
            conn.close()
            if url_data:
                if check_password_hash(url_data[4], password):
                    session['userid'] = url_data[0]
                    session['username'] = url_data[2]
                    return redirect(url_for('home'))
                else:
                    flash("Invalid Password!")
            else:
                flash("User not found! ")
        return render_template('login.html')

# Route for logout page and function
@app.route("/logout", methods=('GET', 'POST'))
def logout():
    session.pop('userid')
    session.pop('username')
    flash("Successfully logged out!")
    return redirect(url_for('login'))

# Route for signup page and function
@app.route("/signup", methods=('GET', 'POST'))
def signup():
    try: 
        session['userid']
        return redirect(url_for('home'))
    except:
        if request.method == 'POST':
            # Get sign up form data
            email = request.form.get('email')
            username = request.form.get('username')
            password = generate_password_hash(request.form.get('password'), method="sha256")
            # Check if email or username already exists
            try:
                conn = connect_db()
                c = conn.cursor()
                c.execute("INSERT into users (email, username, password) VALUES (?, ?, ?)",(email,username,password))
                session['userid'] = c.lastrowid
                conn.commit()
                conn.close()
                session['username'] = username
                return redirect(url_for('home'))
            except sqlite3.Error as err:
                if "username" in str(err):
                    flash("Username already used!")
                elif "email" in str(err):
                    flash("Email already used!")
                else:
                    flash("Oops. Something went wrong, please try again. If the issue persists, please contact support")
        return render_template('signup.html')

