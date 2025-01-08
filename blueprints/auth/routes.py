from flask import render_template, redirect, url_for, flash, session
from extensions import db, bcrypt
from models.user import User
from forms.user_form import UserForm, LoginForm
from . import auth_bp

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = UserForm()
    if form.validate_on_submit():
        hashed_password = Bcrypt().generate_password_hash(form.superPassword.data).decode('utf-8')
        user = User(
            superName=form.superName.data,
            superEmail=form.superEmail.data,
            superPassword=hashed_password,
            superRole='user'
        )
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully!', 'success')
        return redirect(url_for('auth.login'))  # Make sure to use 'auth.login' for login endpoint
    return render_template('register.html', form=form, title="Register")

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(superName=form.superName.data).first()
        if user and bcrypt.check_password_hash(user.superPassword, form.superPassword.data):
            session['user_id'] = user.superID
            session['username'] = user.superName
            flash(f'Welcome {user.superName}!', 'success')
            return redirect(url_for('home.home'))
        else:
            flash('Login failed. Please check your username and password.', 'danger')
    return render_template('login.html', form=form, title="Login")

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))