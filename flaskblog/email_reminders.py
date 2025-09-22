"""
Email reminder functionality for Flask blog
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from flaskblog.models import Review, User, Post

# Email configuration - Update these with your email settings
EMAIL_HOST = 'smtp.gmail.com'  # For Gmail
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USER = 'your-email@gmail.com'  # Replace with your email
EMAIL_PASS = 'your-app-password'      # Replace with your app password


def send_reminder_email(user_email, user_name, post_title, comment_content):
    """
    Send reminder email to user about their comment
    """
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = user_email
        msg['Subject'] = f'Reminder: Your comment on "{post_title}"'
        
        # Email body
        body = f"""
        Hi {user_name},
        
        This is a friendly reminder about your comment on the post "{post_title}".
        
        Your comment:
        "{comment_content}"
        
        Best regards,
        FlaskBlog Team
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        text = msg.as_string()
        server.sendmail(EMAIL_USER, user_email, text)
        server.quit()
        
        print(f"Reminder email sent successfully to {user_email}")
        return True
        
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False


def check_and_send_reminders():
    """
    Check for pending reminders and send emails
    This function should be called periodically (e.g., every minute)
    """
    from flaskblog import db
    
    now = datetime.utcnow()
    
    # Find reviews with reminders that are due and not yet sent
    pending_reminders = Review.query.filter(
        Review.reminder_enabled == True,
        Review.reminder_datetime <= now,
        Review.reminder_sent == False
    ).all()
    
    for review in pending_reminders:
        user = User.query.get(review.user_id)
        post = Post.query.get(review.post_id)
        
        if user and post:
            success = send_reminder_email(
                user.email,
                user.username,
                post.title,
                review.content
            )
            
            if success:
                # Mark reminder as sent
                review.reminder_sent = True
                db.session.commit()
                print(f"Reminder sent for review {review.id}")
            else:
                print(f"Failed to send reminder for review {review.id}")
    
    return len(pending_reminders)


def test_email_reminder():
    """
    Test function to send a sample reminder email
    """
    test_email = "test@example.com"  # Replace with your test email
    return send_reminder_email(
        test_email,
        "Test User",
        "Sample Post",
        "This is a test comment for reminder functionality."
    )


if __name__ == "__main__":
    # Test the email functionality
    print("Testing email reminder...")
    test_email_reminder()