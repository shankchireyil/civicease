
import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request
from flaskblog import app, db, bcrypt
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from flaskblog.models import User, Post, Review, Interest, Notification
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy import func, desc
from datetime import datetime


# ---------------------------------------------------------
# LANDING PAGE
# ---------------------------------------------------------
@app.route("/")
def landing():
    return render_template('landing.html', title='Welcome to CivicEase')


# ---------------------------------------------------------
# DASHBOARD / HOME
# ---------------------------------------------------------
@app.route("/home")
@app.route("/dashboard")
@login_required
def home():
    # Categories with post count
    categories = db.session.query(
        Post.rss_category_id,
        Post.rss_category_name,
        func.count(Post.id).label('count')
    ).filter(
        Post.rss_category_id.isnot(None)
    ).group_by(
        Post.rss_category_id,
        Post.rss_category_name
    ).order_by(Post.rss_category_id).all()

    # Trending (top 5 posts by interests)
    top_posts = db.session.query(
        Post, func.count(Interest.id).label('interest_count')
    ).outerjoin(
        Interest, Interest.post_id == Post.id
    ).group_by(
        Post.id
    ).order_by(
        desc('interest_count')
    ).limit(5).all()

    # Pie chart data
    chart_labels = [post.title for post, c in top_posts]
    chart_values = [c for post, c in top_posts]

    return render_template(
        'home.html',
        categories=categories,
        top_posts=top_posts,
        chart_labels=chart_labels,
        chart_values=chart_values
    )


# ---------------------------------------------------------
# CATEGORY POSTS LIST
# ---------------------------------------------------------
@app.route("/category/<int:category_id>")
@login_required
def category_posts(category_id):
    posts = Post.query.filter_by(rss_category_id=category_id).all()

    if not posts:
        flash("No posts in this category.", "info")
        return redirect(url_for("home"))

    category_name = posts[0].rss_category_name
    return render_template("category_posts.html", posts=posts,
                           category_name=category_name, category_id=category_id)


# ---------------------------------------------------------
# INDIVIDUAL POST VIEW
# ---------------------------------------------------------
@app.route("/post/<int:post_id>")
@login_required
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    reviews = Review.query.filter_by(post_id=post_id).order_by(Review.date_posted.desc()).all()
    return render_template('post.html', post=post, reviews=reviews)


# ---------------------------------------------------------
# REGISTER
# ---------------------------------------------------------
@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationForm()

    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash('Account created! You can now login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', title='Register', form=form)


# ---------------------------------------------------------
# LOGIN
# ---------------------------------------------------------
@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash("Invalid email or password", "danger")

    return render_template("login.html", title="Login", form=form)


# ---------------------------------------------------------
# LOGOUT
# ---------------------------------------------------------
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('landing'))


# ---------------------------------------------------------
# SAVE PROFILE PICTURE
# ---------------------------------------------------------
def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    img = Image.open(form_picture)
    img.thumbnail((125, 125))
    img.save(picture_path)

    return picture_fn


# ---------------------------------------------------------
# ACCOUNT SETTINGS
# ---------------------------------------------------------
@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()

    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file

        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()

        flash("Account updated!", "success")
        return redirect(url_for('account'))

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template("account.html", title="Account",
                           image_file=image_file, form=form)


# ---------------------------------------------------------
# ADD COMMENT + REMINDER
# ---------------------------------------------------------
@app.route("/add_comment", methods=['POST'])
@login_required
def add_comment():
    
    # Get form data
    post_id = request.form.get('post_id')
    comment_text = request.form.get('comment')
    
    if not post_id or not comment_text:
        flash('Invalid comment data', 'danger')
        return redirect(url_for('home'))
    
    # Convert post_id to int and create a new review entry for every submission
    try:
        post_id = int(post_id)
    except (TypeError, ValueError):
        flash('Invalid post id', 'danger')
        return redirect(url_for('home'))

    new_review = Review(
        content=comment_text,
        user_id=current_user.id,
        post_id=post_id,
    )

    db.session.add(new_review)
    db.session.commit()
    flash("Comment saved!", "success")

    return redirect(url_for("post_detail", post_id=post_id))


# ---------------------------------------------------------
# TOGGLE INTEREST (LIKE)
# ---------------------------------------------------------
@app.route("/toggle_interest/<int:post_id>", methods=["POST"])
@login_required
def toggle_interest(post_id):

    existing = Interest.query.filter_by(
        user_id=current_user.id,
        post_id=post_id
    ).first()

    if existing:
        db.session.delete(existing)
        db.session.commit()
        print("Interest removed")
    else:
        new_interest = Interest(user_id=current_user.id, post_id=post_id)
        db.session.add(new_interest)
        db.session.commit()
        print("Interest added")

    return redirect(request.referrer)


@app.route("/my_interests")
@login_required
def my_interests():

    posts = db.session.query(Post).join(Interest).filter(
        Interest.user_id == current_user.id
    ).order_by(Post.rss_category_id).all()

    category_name = "My Interested Services"

    return render_template('my_interests.html', posts=posts, category_name=category_name, category_id=None)

@app.route("/set_notification", methods=['POST'])
@login_required
def set_notification():
    post_id = request.form.get('post_id')
    message = request.form.get('message')
    scheduled_time_str = request.form.get('scheduled_time')

    if not all([post_id, message, scheduled_time_str]):
        flash('Missing information', 'danger')
        return redirect(request.referrer)

    try:
        scheduled_time = datetime.strptime(scheduled_time_str, '%Y-%m-%dT%H:%M')
        post_id = int(post_id)
        
        if scheduled_time < datetime.utcnow():
            flash('Notification time cannot be in the past', 'warning')
            return redirect(request.referrer)

        notif = Notification(
            user_id=current_user.id,
            post_id=post_id,
            message=message,
            scheduled_time=scheduled_time
        )
        db.session.add(notif)
        db.session.commit()
        flash(f'Notification set for {scheduled_time.strftime("%d %b %H:%M")}', 'success')

    except ValueError:
        flash('Invalid date format', 'danger')
    
    return redirect(url_for('post_detail', post_id=post_id))


@app.route("/read_notification/<int:notif_id>")
@login_required
def read_notification(notif_id):
    notif = Notification.query.get_or_404(notif_id)
    if notif.user_id != current_user.id:
        abort(403)
    
    notif.is_read = True
    db.session.commit()
    return redirect(url_for('post_detail', post_id=notif.post_id))

@app.context_processor
def inject_notifications():
    if current_user.is_authenticated:
        unread_notifs = Notification.query.filter(
            Notification.user_id == current_user.id,
            Notification.is_read == False,
            Notification.scheduled_time <= datetime.now()
        ).order_by(Notification.scheduled_time.desc()).all()
        
        return dict(active_notifications=unread_notifs)
    return dict(active_notifications=[])
