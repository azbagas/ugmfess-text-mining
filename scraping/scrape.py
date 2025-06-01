import asyncio
from twscrape import API
from twscrape.logger import set_log_level
import pandas as pd
import json

accounts = []
DELAY_BETWEEN_MONTHS = 10  # seconds
LIMIT_PER_MONTH = 5000  # tweets

# Load json accounts
with open("scraping/accounts.json", "r") as f:
    accounts = json.load(f)
# If accounts.json is empty, exit
if not accounts:
    print("No accounts found in accounts.json. Please add accounts to scrape.")
    exit(1)


async def scrape_tweets(api, start_date, end_date, save_to_file):
    data = []

    # define the search query. Include start date and end date
    q = "from:UGM_FESS since:" + start_date + " until:" + end_date
    print(f"🔎 Scraping tweets: {q}")

    async for tweet in api.search(q, limit=LIMIT_PER_MONTH):
        c = [
            tweet.id,
            tweet.date,
            tweet.url,
            tweet.user.username,
            tweet.rawContent,
            tweet.likeCount,
            tweet.replyCount,
            tweet.retweetCount,
        ]
        data.append(c)

    df = pd.DataFrame(
        data,
        columns=["tweet_id", "time_created", "url", "username", "text", "likes", "replies", "retweets"],
    )

    file_path = "scraping/results/" + save_to_file

    df.to_csv(file_path, index=False)
    print(f"✅ Saved {len(df)} tweets to {file_path}")

    return len(df)


async def main():
    api = API()

    for account in accounts:
        cookies = f"auth_token={account['auth_token']}; ct0={account['ct0']}"
        await api.pool.add_account(
            account["username"],
            account["password"],
            account["email"],
            account["email_password"],
            cookies=cookies,
        )

    await api.pool.login_all()

    set_log_level("INFO")
    print("Starting scraping...")

    # Define the date ranges and corresponding file names
    # end_date is exclusive, so we use the first day of the next month as the end date
    # date_ranges = [
    #     ("2025-01-01", "2025-02-01", "tweets-ugmfess-2025-01.csv"),
    #     ("2025-02-01", "2025-03-01", "tweets-ugmfess-2025-02.csv"),
    #     ("2025-03-01", "2025-04-01", "tweets-ugmfess-2025-03.csv"),
    #     ("2025-04-01", "2025-05-01", "tweets-ugmfess-2025-04.csv"),
    #     ("2025-05-01", "2025-06-01", "tweets-ugmfess-2025-05.csv"),
    # ]
    date_ranges = [
        ("2024-06-01", "2024-07-01", "tweets-ugmfess-2024-06.csv"),
        ("2024-07-01", "2024-08-01", "tweets-ugmfess-2024-07.csv"),
        ("2024-08-01", "2024-09-01", "tweets-ugmfess-2024-08.csv"),
        ("2024-09-01", "2024-10-01", "tweets-ugmfess-2024-09.csv"),
        ("2024-10-01", "2024-11-01", "tweets-ugmfess-2024-10.csv"),
        ("2024-11-01", "2024-12-01", "tweets-ugmfess-2024-11.csv"),
        ("2024-12-01", "2025-01-01", "tweets-ugmfess-2024-12.csv"),
    ]

    total_count = 0
    for start_date, end_date, file_name in date_ranges:
        count = await scrape_tweets(api, start_date, end_date, file_name)
        total_count += count
        print(f"⏳ Waiting {DELAY_BETWEEN_MONTHS} seconds before next month...\n")
        await asyncio.sleep(DELAY_BETWEEN_MONTHS)

    print(f"\n🎉 Scraping completed. Total tweets scraped: {total_count}")


if __name__ == "__main__":
    asyncio.run(main())
