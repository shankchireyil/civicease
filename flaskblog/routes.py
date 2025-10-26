
import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flaskblog import app, db, bcrypt
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from flaskblog.models import User, Post, Review
from flaskblog.email_reminders import check_and_send_reminders
from flask_login import login_user, current_user, logout_user, login_required

@app.route("/")
def landing():
    """Public landing page explaining CivicEase"""
    return render_template('landing.html', title='Welcome to CivicEase')


@app.route("/post/<int:post_id>")
@login_required
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', post=post)

@app.route("/home")
@app.route("/dashboard")
@login_required
def home():
    """Dashboard with government service categories - requires login"""
    # Get all categories with post counts
    categories = db.session.query(
        Post.rss_category_id, 
        Post.rss_category_name,
        db.func.count(Post.id).label('count')
    ).filter(
        Post.rss_category_id.isnot(None)
    ).group_by(
        Post.rss_category_id, 
        Post.rss_category_name
    ).order_by(Post.rss_category_id).all()
    
    return render_template('home.html', categories=categories)


@app.route("/category/<int:category_id>")
@login_required
def category_posts(category_id):
    # Get posts for specific category
    posts = Post.query.filter_by(rss_category_id=category_id).all()
    
    if not posts:
        flash(f'No posts found for category {category_id}', 'info')
        return redirect(url_for('home'))
    
    category_name = posts[0].rss_category_name if posts else f'Category {category_id}'
    return render_template('category_posts.html', posts=posts, 
                         category_name=category_name, category_id=category_id)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


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
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('landing'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


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
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)


@app.route("/add_comment", methods=['POST'])
@login_required
def add_comment():
    from datetime import datetime
    
    # Get form data
    post_id = request.form.get('post_id')
    comment_text = request.form.get('comment')
    reminder_enabled = request.form.get('reminder_enabled') == '1'
    reminder_datetime_str = request.form.get('reminder_datetime')
    
    if not post_id or not comment_text:
        flash('Invalid comment data', 'danger')
        return redirect(url_for('home'))
    
    # Parse reminder datetime if provided
    reminder_datetime = None
    if reminder_enabled and reminder_datetime_str:
        try:
            reminder_datetime = datetime.strptime(reminder_datetime_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            flash('Invalid reminder date format', 'warning')
            reminder_enabled = False
    
    # Check if user already has a review for this post
    existing_review = Review.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    
    if existing_review:
        # Update existing review
        existing_review.content = comment_text
        existing_review.reminder_enabled = reminder_enabled
        existing_review.reminder_datetime = reminder_datetime
        existing_review.reminder_sent = False  # Reset reminder status
        flash('Comment updated!', 'success')
    else:
        # Create new review
        new_review = Review(
            content=comment_text, 
            user_id=current_user.id, 
            post_id=post_id,
            reminder_enabled=reminder_enabled,
            reminder_datetime=reminder_datetime
        )
        db.session.add(new_review)
        flash('Comment saved!', 'success')
    
    db.session.commit()
    return redirect(url_for('home'))



@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))


@app.route("/check_reminders")
@login_required
def check_reminders_route():
    """
    Manual route to check and send pending reminders (for testing)
    """
    try:
        count = check_and_send_reminders()
        flash(f'Checked reminders: {count} reminders processed', 'info')
    except Exception as e:
        flash(f'Error checking reminders: {str(e)}', 'danger')
    return redirect(url_for('home'))
