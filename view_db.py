#!/usr/bin/env python3
"""
Simple database viewer using Flask app context and SQLAlchemy
"""

from flaskblog import app, db
from flaskblog.models import User, Post, Review


def show_table_data(model_class, table_name, limit=10):
    """Show data from a SQLAlchemy model"""
    with app.app_context():
        print(f"\n{'='*60}")
        print(f"TABLE: {table_name.upper()}")
        print(f"{'='*60}")
        
        # Get total count
        total = model_class.query.count()
        print(f"Total rows: {total}")
        
        if total == 0:
            print("No data found")
            return
        
        # Get limited rows
        rows = model_class.query.limit(limit).all()
        print(f"Showing first {len(rows)} rows:")
        print("-" * 60)
        
        for i, row in enumerate(rows, 1):
            print(f"Row {i}: {row}")
        
        return rows


def show_post_details(limit=5):
    """Show Post table with RSS details"""
    with app.app_context():
        print(f"\n{'='*80}")
        print("POST TABLE - RSS DATA DETAILS")
        print(f"{'='*80}")
        
        posts = Post.query.limit(limit).all()
        
        if not posts:
            print("No posts found")
            return
        
        for post in posts:
            print(f"ID: {post.id}")
            print(f"Title: {post.title}")
            print(f"RSS Category ID: {post.rss_category_id}")
            print(f"RSS Category: {post.rss_category_name}")
            print(f"RSS Link: {post.rss_link}")
            print(f"RSS Description: {post.rss_description}")
            print(f"RSS PubDate: {post.rss_pubDate}")
            print("-" * 60)


def show_rss_summary():
    """Show summary of RSS data by category"""
    with app.app_context():
        print(f"\n{'='*60}")
        print("RSS CATEGORIES SUMMARY")
        print(f"{'='*60}")
        
        # Get distinct categories
        from sqlalchemy import func
        categories = db.session.query(
            Post.rss_category_id,
            Post.rss_category_name,
            func.count(Post.id).label('count')
        ).filter(
            Post.rss_category_id.isnot(None)
        ).group_by(
            Post.rss_category_id,
            Post.rss_category_name
        ).all()
        
        if not categories:
            print("No RSS data found")
            return
        
        for cat_id, cat_name, count in categories:
            print(f"Category {cat_id}: {cat_name} - {count} items")


def main():
    """Main function - show all available data"""
    print("Flask Database Viewer")
    print("="*60)
    
    # Show all tables
    show_table_data(User, "user", 10)
    show_table_data(Post, "post", 10)  
    show_table_data(Review, "review", 10)
    
    # Show detailed RSS data
    show_post_details(5)
    
    # Show RSS summary
    show_rss_summary()


if __name__ == "__main__":
    main()