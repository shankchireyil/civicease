"""Import RSS JSON files from `rss_data/` into the Post table.

Creates Post rows with RSS fields filled. Uses app context and SQLAlchemy session.
"""
import json
import glob
from datetime import datetime
from flaskblog import app, db
from flaskblog.models import Post
import time


def parse_pubdate(s):
    if not s:
        return None
    # Try common RSS date format
    for fmt in ("%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S"):
        try:
            return datetime.strptime(s, fmt)
        except Exception:
            continue
    return None


def import_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    cat_id = data.get('category_id')
    items = data.get('items', [])

    inserted = 0
    skipped = 0
    for it in items:
        title = it.get('title') or ''
        link = it.get('link') or ''
        desc = it.get('description') or ''
        pub = parse_pubdate(it.get('pubDate'))
        cat_name = it.get('category') or ''

        # Truncate title to match database constraint
        truncated_title = title[:100] if title else 'Untitled'
        
        # Check if post with this title already exists
        existing_post = Post.query.filter_by(title=truncated_title).first()
        if existing_post:
            skipped += 1
            continue

        post = Post(
            title=truncated_title,
            rss_category_id=cat_id,
            rss_category_name=cat_name,
            rss_link=link,
            rss_description=desc,
            rss_pubDate=pub
        )
        db.session.add(post)
        inserted += 1
    
    db.session.commit()
    return inserted, skipped


def run_import_cycle():
    imported_total = 0
    skipped_total = 0
    with app.app_context():
        files = glob.glob('rss_data/*.json')
        print(f'Found {len(files)} rss JSON files')
        for p in files:
            print('Importing', p)
            try:
                inserted, skipped = import_file(p)
                print(f'  -> Inserted {inserted} rows, skipped {skipped} duplicates')
                imported_total += inserted
                skipped_total += skipped
            except Exception as e:
                print('  -> Error importing', p, e)

    print(f'Done. Total rows inserted: {imported_total}, Total duplicates skipped: {skipped_total}')


