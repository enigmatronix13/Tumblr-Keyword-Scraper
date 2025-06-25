#!/usr/bin/env python3
"""
Tumblr Post and Comment Scraper
Scrapes Tumblr posts based on tags or blog posts containing specific keywords.
"""

import os
import sys
import json
import csv
import time
import argparse
from datetime import datetime
from typing import List, Dict
import logging

try:
    import pytumblr
    from config_template import *
except ImportError as e:
    print(f"Missing dependencies: {e}")
    print("Please install requirements: pip install -r requirements.txt")
    sys.exit(1)

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tumblr_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Default keywords and blogs
KEYWORDS = ["keyword1", "keyword2", "keyword3"]
BLOGS = {
    "blog1.tumblr.com": KEYWORDS,
    "blog2.tumblr.com": KEYWORDS,
    "blog3.tumblr.com": KEYWORDS
}

OUTPUT_DIRECTORY = "output"
RATE_LIMIT_DELAY = 1.2  # API rate delay in seconds

class TumblrScraper:
    def __init__(self, consumer_key=None, consumer_secret=None, oauth_token=None, oauth_token_secret=None):
        # Load API credentials
        self.consumer_key = consumer_key or os.getenv('TUMBLR_CONSUMER_KEY', TUMBLR_CONSUMER_KEY)
        self.consumer_secret = consumer_secret or os.getenv('TUMBLR_CONSUMER_SECRET', TUMBLR_CONSUMER_SECRET)
        self.oauth_token = oauth_token or os.getenv('TUMBLR_OAUTH_TOKEN', TUMBLR_OAUTH_TOKEN)
        self.oauth_token_secret = oauth_token_secret or os.getenv('TUMBLR_OAUTH_TOKEN_SECRET', TUMBLR_OAUTH_TOKEN_SECRET)

        self.api_client = None
        if self.consumer_key and self.consumer_secret:
            self.api_client = pytumblr.TumblrRestClient(
                self.consumer_key, self.consumer_secret, self.oauth_token, self.oauth_token_secret
            )
            logger.info("Tumblr API client initialized")

        os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)

    def search_tagged_posts_api(self, tag: str, limit: int = 100) -> List[Dict]:
        if not self.api_client:
            logger.error("API client not available")
            return []

        posts = []
        before_timestamp = None
        collected = 0

        while collected < limit:
            try:
                response = self.api_client.tagged(tag, before=before_timestamp, limit=20)
                if not response:
                    break
                for post in response:
                    if collected >= limit:
                        break
                    post_data = self._extract_api_post_data(post)
                    posts.append(post_data)
                    collected += 1
                before_timestamp = response[-1].get('timestamp')
                time.sleep(RATE_LIMIT_DELAY)
            except Exception as e:
                logger.error(f"Error in API call: {e}")
                break

        return posts

    def search_blog_posts_api(self, blog_name: str, keywords: List[str], limit: int = 100) -> List[Dict]:
        if not self.api_client:
            logger.error("API client not available")
            return []

        posts = []
        offset = 0
        batch_size = 20

        while len(posts) < limit:
            try:
                blog_posts = self.api_client.posts(blog_name, offset=offset, limit=batch_size)
                if not blog_posts.get('posts'):
                    break
                for post in blog_posts['posts']:
                    if self._post_contains_keywords(post, keywords):
                        post_data = self._extract_api_post_data(post)
                        post_data['matched_keywords'] = self._get_matched_keywords(post, keywords)
                        posts.append(post_data)
                        if len(posts) >= limit:
                            break
                offset += batch_size
                time.sleep(RATE_LIMIT_DELAY)
            except Exception as e:
                logger.error(f"Error searching blog: {e}")
                break

        return posts

    def _post_contains_keywords(self, post: Dict, keywords: List[str]) -> bool:
        text = self._get_post_text_content(post).lower()
        return any(kw.lower() in text for kw in keywords)

    def _get_matched_keywords(self, post: Dict, keywords: List[str]) -> List[str]:
        text = self._get_post_text_content(post).lower()
        return [kw for kw in keywords if kw.lower() in text]

    def _get_post_text_content(self, post: Dict) -> str:
        # Combine relevant textual fields
        parts = []
        if post.get('type') == 'text':
            parts.extend([post.get('title', ''), post.get('body', '')])
        elif post.get('type') == 'photo':
            parts.append(post.get('caption', ''))
        elif post.get('type') == 'quote':
            parts.extend([post.get('text', ''), post.get('source', '')])
        parts.extend(post.get('tags', []))
        parts.append(post.get('summary', ''))
        return ' '.join(filter(None, parts))

    def _extract_api_post_data(self, post: Dict) -> Dict:
        # Extract and structure key post data
        return {
            'id': post.get('id'),
            'blog_name': post.get('blog_name'),
            'post_url': post.get('post_url'),
            'type': post.get('type'),
            'timestamp': post.get('timestamp'),
            'date': post.get('date'),
            'tags': post.get('tags', []),
            'note_count': post.get('note_count', 0),
            'summary': post.get('summary', ''),
            'title': post.get('title', '') if post.get('type') == 'text' else '',
            'body': post.get('body', '') if post.get('type') == 'text' else '',
            'caption': post.get('caption', '') if post.get('type') == 'photo' else '',
            'text': post.get('text', '') if post.get('type') == 'quote' else '',
            'source': post.get('source', '') if post.get('type') == 'quote' else '',
            'scraped_at': datetime.now().isoformat()
        }

    def save_posts_to_csv(self, posts: List[Dict], filename: str) -> str:
        if not posts:
            return ""
        filepath = os.path.join(OUTPUT_DIRECTORY, filename)
        keys = sorted(set(k for p in posts for k in p.keys()))
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            for p in posts:
                row = {k: (', '.join(v) if isinstance(v, list) else str(v)) for k, v in p.items()}
                writer.writerow(row)
        return filepath

    def save_posts_to_json(self, posts: List[Dict], filename: str) -> str:
        if not posts:
            return ""
        filepath = os.path.join(OUTPUT_DIRECTORY, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(posts, f, indent=2, ensure_ascii=False)
        return filepath

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tag', type=str)
    parser.add_argument('--blog', type=str)
    parser.add_argument('--keywords', nargs='+')
    parser.add_argument('--limit', type=int, default=50)
    parser.add_argument('--output', type=str)
    parser.add_argument('--format', choices=['csv', 'json'], default='csv')
    args = parser.parse_args()

    scraper = TumblrScraper()
    posts = []

    if args.tag:
        posts = scraper.search_tagged_posts_api(args.tag, args.limit)
    elif args.blog and args.keywords:
        posts = scraper.search_blog_posts_api(args.blog, args.keywords, args.limit)
    else:
        for blog, kw in BLOGS.items():
            posts = scraper.search_blog_posts_api(blog, kw, args.limit)
            if posts:
                fname = f"{blog.replace('.', '_')}_posts.{args.format}"
                if args.format == 'json':
                    scraper.save_posts_to_json(posts, fname)
                else:
                    scraper.save_posts_to_csv(posts, fname)

    if posts and args.blog:
        fname = args.output or f"tumblr_posts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{args.format}"
        if args.format == 'json':
            scraper.save_posts_to_json(posts, fname)
        else:
            scraper.save_posts_to_csv(posts, fname)
        print(f"Saved {len(posts)} posts to {fname}")

if __name__ == "__main__":
    main()
