# Tumblr Scraper 

A Python-based Tumblr scraper that collects posts containing specified keywords from Tumblr blogs using the official Tumblr API. Supports saving results to CSV or JSON formats with configurable filtering options.

## Features

- Scrape posts by tag or from specific blogs
- Keyword filtering with case sensitivity options
- Multiple output formats (CSV, JSON)
- API rate limiting and error handling
- Progress tracking and comprehensive logging
- Configurable via command-line arguments

## Setup

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Configure API Keys
1. Register at [Tumblr OAuth Apps](https://www.tumblr.com/oauth/apps)
2. Edit `config_template.py`:

```python
TUMBLR_CONSUMER_KEY = "your_consumer_key"
TUMBLR_CONSUMER_SECRET = "your_consumer_secret"
TUMBLR_OAUTH_TOKEN = "your_oauth_token"
TUMBLR_OAUTH_TOKEN_SECRET = "your_oauth_token_secret"
```

## Usage

```bash
python tumblr_scraper.py
```

### Options

| Option | Description | Example |
|--------|-------------|---------|
| `--tag TAG` | Scrape posts with specific tag | `--tag photography` |
| `--blog BLOG` | Target specific blog | `--blog myblog.tumblr.com` |
| `--keywords KW1 KW2` | Filter by keywords | `--keywords cat dog` |
| `--limit N` | Maximum posts to fetch (default: 50) | `--limit 100` |
| `--output FILE` | Output filename | `--output results.csv` |
| `--format FORMAT` | Output format: csv or json (default: csv) | `--format json` |
| `--case-sensitive` | Enable case-sensitive matching | |
| `--exact-match` | Require exact keyword matches | |
| `--min-notes N` | Minimum engagement threshold | `--min-notes 10` |
| `--exclude-reblogs` | Skip reblogged content | |

### Examples

**Scrape posts by tag:**
```bash
python tumblr_scraper.py --tag "digital art" --limit 100 --format json
```

**Scrape specific blog with keywords:**
```bash
python tumblr_scraper.py --blog coolblog.tumblr.com --keywords "travel" "photography" --limit 50
```

**Advanced filtering:**
```bash
python tumblr_scraper.py --tag music --exact-match --min-notes 25 --exclude-reblogs --limit 200
```

**Use default configuration:**
```bash
python tumblr_scraper.py
```

## Configuration

### Default Settings
Edit these constants in the script for default behavior:

```python
KEYWORDS = [
    "keyword1", "keyword2", "keyword3"
]
```
```
BLOGS = {
    "blog1.tumblr.com": KEYWORDS,
    "blog2.tumblr.com": KEYWORDS,
}
```

## Output

### File Structure
- Files saved in `output/` directory
- Auto-generated filenames: `tumblr_posts_YYYYMMDD_HHMMSS.csv`
- Tag-based: `tag_photography_20240625.json`
- Blog-based: `blog_name_posts.csv`

### Data Fields
Each post includes:
- `id`, `blog_name`, `post_url`, `type`, `timestamp`, `date`
- `title`, `body`, `caption`, `summary`, `tags`
- `note_count`, `matched_keywords`, `scraped_at`
- `is_reblog`, `reblog_key`

## Troubleshooting

**Authentication Issues**
- Verify API credentials
- Check if OAuth tokens are valid
- Ensure app registration is active

**Rate Limiting**
- Script automatically handles API limits
- Increase delay with custom rate limiting if needed
- Default delay: 1.2 seconds between requests

**Empty Results**
- Verify blog names include `.tumblr.com`
- Check keyword specificity
- Try broader search terms

**Network Errors**
- Check internet connection
- Verify firewall settings
- Review `tumblr_scraper.log` for details

## API Limits

- Respect Tumblr's rate limits (300 requests per hour for most endpoints)
- Script includes automatic rate limiting
- Monitor API usage to avoid quota exhaustion
- Consider running scrapes during off-peak hours

## Best Practices

- Use specific keywords to reduce noise
- Batch processing with reasonable limits (50-200 posts)
- Regular backups of important datasets
- Follow Tumblr's Terms of Service
- Respect content creators' rights

## Files Generated

- `tumblr_scraper.log` - Activity and error log
- `output/*.csv` or `output/*.json` - Scraped data
- `config_template.py` - API configuration (create if missing)

## Requirements

- Python 3.7+
- Valid Tumblr API credentials
- Internet connection
- Required packages: pytumblr, requests
