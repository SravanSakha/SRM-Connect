from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "srm_secret_key"

# ---------- DATABASE INIT ----------
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            password TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS interests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            interest TEXT
        )
    ''')

    conn.commit()
    conn.close()

# ---------- HOME ----------
@app.route('/')
def home():
    return render_template("index.html")

# ---------- REGISTER ----------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                       (name, email, password))
        conn.commit()
        conn.close()

        return redirect('/login')

    return render_template("register.html")

# ---------- LOGIN ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email=? AND password=?",
                       (email, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user_id'] = user[0]
            return redirect('/dashboard')

    return render_template("login.html")

# ---------- DASHBOARD ----------
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST':
        interests = request.form.getlist('interests')

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        for interest in interests:
            cursor.execute("INSERT INTO interests (user_id, interest) VALUES (?, ?)",
                           (session['user_id'], interest))

        conn.commit()
        conn.close()

        return redirect('/matches')

    return render_template("dashboard.html")

# ---------- MATCHES ----------
@app.route('/matches')
def matches():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT u2.name
        FROM interests i1
        JOIN interests i2 ON i1.interest = i2.interest
        JOIN users u2 ON i2.user_id = u2.id
        WHERE i1.user_id = ?
        AND u2.id != ?
    """, (session['user_id'], session['user_id']))

    matches = cursor.fetchall()
    conn.close()

    return render_template("matches.html", matches=matches)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
