from flaskblog import db, app  # replace with your actual app/db names
with app.app_context():
    db.create_all()