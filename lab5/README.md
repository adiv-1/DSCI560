# Lab 5 — Reddit scraper (requests + BeautifulSoup)

This scraper collects up to 100 **self posts** from `r/datascience` using `old.reddit.com` and writes them to `output.csv`.

## Setup (Ubuntu / Python)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

From the `lab5/` directory:

```bash
python3 reddit_scraper.py
```

Provide up to 2 positional args: `subreddit` and `output`:

```bash
python3 reddit_scraper.py
python3 reddit_scraper.py python
python3 reddit_scraper.py python python_posts.csv
```

Output: `output.csv` with columns:

- `#` (row number)
- `title`
- `author`
- `score`
- `num_comments`
- `permalink`

## Large requests / rate limits / timeouts

For large scrapes (hundreds/thousands of posts), the script already includes:
- a request timeout
- a delay between pages
- automatic retry/backoff on HTTP 429 (rate limiting)

If you need more than 100 posts, change the `LIMIT` constant inside `reddit_scraper.py`.

## Notes

- This uses `old.reddit.com` because it is easier to parse with BeautifulSoup than the modern UI.
- The script includes a small retry/backoff when Reddit responds with HTTP 429 (rate limiting).
