from flask import Flask, render_template, request, url_for, session, flash, redirect
import sqlite3

app = Flask(__name__)
app.secret_key = "asdfasddfasldkfjlöakasdkföljalksdjfölkads"


def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS countries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            country TEXT NOT NULL,
            status TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route("/add-country", methods=["POST"])
def add_country():
    if "email" in session:
        country = request.form["country"]
        status = request.form["status"]
        email = session["email"]

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM user WHERE email = ?', (email,))
        result = cursor.fetchone()
        if result is None:
            conn.close()
            return {"error"}, 404

        user_id = result[0]
        conn.close()

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT status FROM countries WHERE user_id = ? AND country = ?', (user_id, country))
        existing_entry = cursor.fetchone()
        conn.close()

        conn = sqlite3.connect('database.db')
        if existing_entry:
            cursor = conn.cursor()
            cursor.execute('UPDATE countries SET status = ? WHERE user_id = ? AND country = ?', (status, user_id, country))
            conn.commit()
            conn.close()
        else:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO countries (user_id, country, status) VALUES (?, ?, ?)', (user_id, country, status))
            conn.commit()
            conn.close()

        return 'Country added', 200
    else:
        return redirect(url_for("login"))

@app.route("/api-get-visited-countries")
def get_visited_countries():
    if "email" not in session:
        return {"error": "Not logged in"}, 401
        
    email = session["email"]
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT id FROM user WHERE email = ?', (email,))
    user_id = cursor.fetchone()[0]
    
    cursor.execute('SELECT country, status FROM countries WHERE user_id = ?', (user_id,))
    countries = cursor.fetchall()
    conn.close()
    
    return {"countries": [{"country": c[0], "status": c[1]} for c in countries]}



@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM user WHERE email = ?', (email,))
        existing_user = cursor.fetchone()
        if existing_user:
            flash('Email address already registered')
            return redirect(url_for("signup"))
        conn.close()
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO user (email, password) VALUES (?, ?)
        ''', (email, password))
        conn.commit()
        conn.close()
        email = request.form["email"]
        password = request.form["password"]
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM user WHERE email = ? AND password = ?', (email, password))
        existing_user = cursor.fetchone()
        conn.close()
        if existing_user:
            session["email"] = email
            return redirect(url_for("index"))
        else:
            flash('Incorrect email or password')
            return redirect(url_for("login"))
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM user WHERE email = ? AND password = ?', (email, password))
        existing_user = cursor.fetchone()
        conn.close()
        if existing_user:
            session["email"] = email
            return redirect(url_for("index"))
        else:
            flash('Incorrect email or password')
            return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/")
def index():
    if "email" in session:
        return render_template("index.html")
    else:
        return redirect(url_for("login"))
    
@app.route("/logout")
def logout():
    session.pop("email", None)
    return redirect(url_for("login"))
@app.route("/delete-account")
def del_account_ask():
    return '<a href="/delete-account-confirm">Click here to delete your account forever.</a>'

@app.route("/delete-account-confirm")
def delete_account_confirmed():
    if "email" in session:
        email = session["email"]
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM user WHERE email = ?', (email,))
        conn.commit()
        conn.close()
        session.pop("email", None)
        flash('Your account has been deleted')
        return redirect(url_for("signup"))
    else:
        return redirect(url_for("login"))
    


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)