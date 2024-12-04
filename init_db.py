from app import app, db, bcrypt, User

# Create a test user
with app.app_context():
    if User.query.first() is None:
        hashed_password = bcrypt.generate_password_hash('PASSWORD').decode('utf-8')
        admin_user = User(username='admin', password=hashed_password, role='admin')
        db.session.add(admin_user)
        db.session.commit()
        print("Admin user created: admin / PASSWORD")
    else:
        print("Users already exist in the database.")
