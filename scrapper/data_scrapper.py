#!/usr/bin/env python3
"""
Simple RSS scraper for all India Government RSS categories
Scrapes categories 1-13 and saves each to separate JSON files
"""

import requests
import json
import xml.etree.ElementTree as ET
import os
from datetime import datetime
import time


def scrape_category(cat_id):
    """Scrape a single RSS category and return parsed data"""
    url = f"https://services.india.gov.in/feed/rss?cat_id={cat_id}&ln=en"
    
    try:
        # Fetch RSS feed
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Parse XML
        root = ET.fromstring(response.content)
        channel = root.find('channel')
        
        if channel is None:
            return None
            
        # Extract data
        category_title = getattr(channel.find('title'), 'text', '')
        data = {
            'category_id': cat_id,
            'category_name': category_title,
            'title': category_title,
            'description': getattr(channel.find('description'), 'text', ''),
            'scraped_at': datetime.now().isoformat(),
            'items': []
        }
        
        # Extract items
        for item in channel.findall('item'):
            item_data = {
                'title': getattr(item.find('title'), 'text', ''),
                'link': getattr(item.find('link'), 'text', ''),
                'description': getattr(item.find('description'), 'text', ''),
                'pubDate': getattr(item.find('pubDate'), 'text', ''),
                'category': getattr(item.find('category'), 'text', '')
            }
            data['items'].append(item_data)
        
        return data
        
    except Exception as e:
        print(f"Error scraping category {cat_id}: {e}")
        return None


def save_to_json(data, cat_id):
    """Save data to JSON file in subfolder"""
    # Create subfolder if it doesn't exist
    folder = "rss_data"
    os.makedirs(folder, exist_ok=True)
    
    filename = os.path.join(folder, f"category_{cat_id}.json")
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return filename
    except Exception as e:
        print(f"Error saving category {cat_id}: {e}")
        return None


def run_scrapper():
    """Main scraper function"""
    print("Starting India Government RSS scraper for all categories...")
    
    results = []
    
    # Scrape categories 1-13
    for cat_id in range(1, 14):
        print(f"Scraping category {cat_id}...")
        
        data = scrape_category(cat_id)
        if data and data['items']:
            filename = save_to_json(data, cat_id)
            if filename:
                results.append({
                    'category_id': cat_id,
                    'category_name': data['category_name'],
                    'title': data['title'],
                    'items_count': len(data['items']),
                    'filename': filename
                })
                print(f"  ✓ Saved {len(data['items'])} items to {filename}")
        else:
            print(f"  ✗ No data found for category {cat_id}")
    
    # Summary
    print(f"\n{'='*50}")
    print("SCRAPING SUMMARY")
    print(f"{'='*50}")
    print(f"Total categories processed: {len(results)}")
    
    for result in results:
        print(f"Category {result['category_id']:2d}: {result['items_count']} items - {result['category_name']} - {result['filename']}")
    
    print(f"\nTotal files created: {len(results)}")


