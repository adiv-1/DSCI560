import praw
import pandas as pd
import time

# Initialize Reddit instance with credentials
# Unable to get cliend_id and client_secret so will ask in office hours tomorrow
reddit = praw.Reddit(
    client_id=client_id,
    client_secret=client_secret,
)

subreddit_name = 'tech' # Change later
limit = 10 # Scrape this number of posts from the subreddit
subreddit = reddit.subreddit(subreddit_name)

post_data = []
print(f"Scraping top {limit} posts from r/{subreddit_name}...")

for submission in subreddit.top(limit=limit):
    post_data.append({
        'Title': submission.title,
        'Author': submission.author.name if submission.author else 'N/A',
        'Score': submission.score,
        'URL': submission.url,
        'Comments': submission.num_comments
    })
    # Add a delay to avoid rate limits
    time.sleep(1) 

# Create dataframe with scraped data
df = pd.DataFrame(post_data)
print("\nScraping complete:")
print(df.head())

# Output to CSV
df.to_csv(f'{subreddit_name}_posts.csv', index=False)
print(f"\nData saved to {subreddit_name}_posts.csv")
