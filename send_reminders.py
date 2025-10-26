"""
Standalone process to check for pending review reminders and send emails to users.
Run this script periodically (e.g., via cron or Task Scheduler).
"""
import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from flaskblog import app, db
from flaskblog.models import User, Post, Review


# --- CONFIGURE YOUR SMTP SETTINGS HERE ---
SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
SMTP_USER = os.environ.get('SMTP_USER', 'your_email@gmail.com')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', 'your_app_password')
FROM_EMAIL = os.environ.get('FROM_EMAIL', SMTP_USER)

print(SMTP_USER)


def send_email(to_email, subject, body):
    msg = MIMEText(body, 'plain', 'utf-8')
    msg['Subject'] = subject
    msg['From'] = FROM_EMAIL
    msg['To'] = to_email
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(FROM_EMAIL, [to_email], msg.as_string())


import time

def process_reminders():
    now = datetime.now()
    with app.app_context():
        reviews = Review.query.filter(
            Review.reminder_enabled == True,
            Review.reminder_sent == False,
            Review.reminder_datetime != None,
            Review.reminder_datetime <= now
        ).all()
        if reviews:
            print(f"Found {len(reviews)} reminders to send.")
        for review in reviews:
            user = User.query.get(review.user_id)
            post = Post.query.get(review.post_id)
            if not user or not user.email:
                print(f"Skipping review {review.id}: user or email not found.")
                continue
            subject = f"CivicEase Reminder: {post.title if post else 'Post'}"
            body = f"Hello {user.username},\n\nThis is your reminder for the post: {post.title if post else 'Post'}\n\nYour comment: {review.content}\n\nVisit CivicEase for more details.\n\n-- CivicEase Team"
            try:
                send_email(user.email, subject, body)
                review.reminder_sent = True
                db.session.commit()
                print(f"Sent reminder to {user.email} for review {review.id}")
            except Exception as e:
                print(f"Failed to send email to {user.email}: {e}")

def main():
    print("Reminder service started. Checking every 20 seconds...")
    while True:
        process_reminders()
        time.sleep(20)

if __name__ == "__main__":
    main()
