from flask import Flask, render_template, request, redirect, session
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = os.environ.get('SECRET_KEY', 'dev_key_for_local_testing')

# Create database
def create_database():
    conn = sqlite3.connect('students.db')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

create_database()


@app.route('/')
def home():
    return render_template('home.html')


# Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            return "Passwords do not match!"

        hashed_password = generate_password_hash(password)

        try:
            conn = sqlite3.connect('students.db')
            conn.execute(
                'INSERT INTO students (name, email, password) VALUES (?, ?, ?)',
                (name, email, hashed_password)
            )
            conn.commit()
            conn.close()

            return "Registration Successful!"

        except sqlite3.IntegrityError:
            return "Email already registered!"

    return render_template('register.html')


# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('students.db')
        conn.row_factory = sqlite3.Row

        student = conn.execute(
            'SELECT * FROM students WHERE email = ?',
            (email,)
        ).fetchone()

        conn.close()

        if student and check_password_hash(student['password'], password):
            session['student_name'] = student['name']
            session['student_id'] = student['id']
            session['student_email'] = student['email']
            return redirect('/dashboard')

        return "Invalid email or password!"

        return "Invalid email or password!"

    return render_template('login.html')


# Dashboard
@app.route('/dashboard')
def dashboard():
    if 'student_name' not in session:
        return redirect('/login')

    return render_template('dashboard.html',
                           name=session['student_name'])

# Profile
@app.route('/profile')
def profile():
    if 'student_name' not in session:
        return redirect('/login')

    return render_template(
        'profile.html',
        name=session['student_name'],
        student_id=session['student_id'],
        email=session['student_email']
    )

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)