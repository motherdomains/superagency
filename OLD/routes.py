from flask import render_template, request, redirect, url_for, flash
from models import User
from extensions import db, bcrypt

print("Routes file loaded!")  # Print to confirm the routes are being loaded

# Route: Home
def home():
    print("Home route is being accessed")  # Debug line
    return render_template('index.html')

# Route: Login
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            flash('Logged in successfully!', 'success')
            return redirect(url_for('home'))
        flash('Invalid credentials, please try again.', 'danger')
    return render_template('login.html')

# Route: Register
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # Add user to database
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')