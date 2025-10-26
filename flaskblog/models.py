from datetime import datetime
from flaskblog import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):

    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)

    reviews = db.relationship('Review', back_populates='user')

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Post(db.Model):

    __tablename__ = 'post'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    # RSS fields
    rss_category_id = db.Column(db.Integer, nullable=True)
    rss_category_name = db.Column(db.String(120), nullable=True)
    rss_link = db.Column(db.String(300), nullable=True)
    rss_description = db.Column(db.Text, nullable=True)
    rss_pubDate = db.Column(db.DateTime, nullable=True)
    # date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    # content = db.Column(db.Text, nullable=False)
    reviews = db.relationship('Review', back_populates='post')

    def __repr__(self):
        return f"Post(id={self.id}, title='{self.title}', rss_cat={self.rss_category_id})"


class Review(db.Model):

    __tablename__ = 'review'

    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    
    # Reminder fields
    reminder_enabled = db.Column(db.Boolean, nullable=False, default=False)
    reminder_datetime = db.Column(db.DateTime, nullable=True)
    reminder_sent = db.Column(db.Boolean, nullable=False, default=False)

    post = db.relationship('Post', back_populates='reviews')
    user = db.relationship('User', back_populates='reviews')

    def __repr__(self):
        return f"Review('user : {self.user_id}', 'post : {self.post_id}\nreview : {self.content}')"
    
    
