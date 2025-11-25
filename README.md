# CivicEase - Civic Information Aggregator
## Overview

**CivicEase** is a Flask web application designed to aggregate civic and government service announcements from RSS-style JSON feeds. It provides a user-friendly dashboard where citizens can browse categorized posts, add comments with optional email reminders, and manage their accounts.

## Code Organization

### Project Structure

```
d:\software_lab\
├── run.py                      # Application entrypoint
├── data_refresh.py             # Data refresh utility
├── Makefile                    # Build/task automation
├── rss_data/                   # RSS JSON files directory
├── instance/                   # Flask instance folder (DB, config)
├── civic_app/                  # Main application package
│   ├── __init__.py            # App factory & initialization
│   ├── routes.py              # Web route handlers
│   ├── models.py              # SQLAlchemy models
│   ├── forms.py               # WTForms definitions
│   ├── static/                # Static assets (CSS, JS, images)
│   │   ├── main.css
│   │   ├── css/               # Bootstrap CSS
│   │   ├── js/                # Bootstrap JS
│   │   └── profile_pics/      # User uploaded images
│   └── templates/             # Jinja2 templates
│       ├── layout.html        # Base template
│       ├── landing.html       # Public landing page
│       ├── home.html          # Dashboard
│       ├── post.html          # Post detail page
│       ├── category_posts.html# Category listing
│       ├── account.html       # User account
│       ├── login.html         # Login form
│       └── register.html      # Registration form
└── scrapper/                   # RSS scraping package
    ├── __init__.py            # Package initialization
    ├── scraper.py             # RSS feed scraper logic
    └── processor.py           # Data processing utilities
```

## Role of Each File

### Root Level Files

| File | Purpose |
|------|---------|
| `run.py` | Starts the Flask development server |
| `data_refresh.py` | Refreshes or updates data |
| `Makefile` | Build and task automation |

### civic_app/ Package

| File | Purpose |
|------|---------|
| `__init__.py` | Flask app factory and extension initialization (db, bcrypt, login_manager) |
| `routes.py` | Core routing logic with all endpoints (auth, dashboard, posts, comments) |
| `models.py` | SQLAlchemy models: User, Post, Review (comments) |
| `forms.py` | WTForms validation for registration, login, account updates |
| `templates/` | Jinja2 HTML templates for all pages |
| `static/` | CSS, JavaScript, and uploaded profile images |

### scrapper/ Package

| File | Purpose |
|------|---------|
| `__init__.py` | Package initialization |
| `scraper.py` | RSS feed scraper logic for fetching feed data |
| `processor.py` | Data processing utilities for transforming feed content |

### Key Route Functions

- **`post_detail`**: Fetches a post and its reviews (comments) sorted newest-first
- **`add_comment`**: Creates new Review entries; allows multiple comments per user/post
- **`register`, `login`, `logout`**: User authentication
- **`account`**: Profile management and image upload

## Problem Statement

Build a civic information aggregator that:
1. Ingests RSS-style JSON feeds of government announcements into a database
2. Provides a categorized dashboard for browsing posts
3. Enables user registration and account management
4. Allows users to comment on posts with optional email reminders

## Scope

### Implemented

- RSS JSON import with title-based duplicate detection
- Category-based content browsing
- User registration, login, profile management
- Comment system with multiple comments per user/post
- Email reminder scheduling and delivery
- Profile image upload with thumbnail generation
- Responsive Bootstrap UI

### Not Implemented

- Comment editing/deletion
- Comment threading or moderation


## How It Works

1. RSS scraper fetches feeds and stores as JSON in `rss_data/`
2. Import script reads JSON, checks for duplicates, and inserts Post records
3. Users register and login to the web dashboard
4. Users browse posts by category and add comments
5. Comment reminders are scheduled and sent via email

## Quick Start

```bash
# Start the app
make start_app

#start data refresh
make data_refresh


Open `http://localhost:5000` in your browser.

## Technology Stack

- **Backend**: Python, Flask, SQLAlchemy
- **Frontend**: Jinja2, Bootstrap 4, HTML/CSS
- **Database**: SQLite
- **Authentication**: Flask-Login, Bcrypt
- **Forms**: WTForms
- **Email**: SMTP integration
- **Images**: Pillow

---


