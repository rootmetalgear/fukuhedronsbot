import tweepy
import requests
import time
import os
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# API Credentials
TWITTER_API_KEY = os.environ.get('TWITTER_API_KEY')
TWITTER_API_SECRET = os.environ.get('TWITTER_API_SECRET')
TWITTER_ACCESS_TOKEN = os.environ.get('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_TOKEN_SECRET = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')

# Magic Eden API
BASE_API_URL = "https://api-mainnet.magiceden.dev/v2/ord"
COLLECTION_NAME = "fukuhedrons"
API_KEY = os.environ.get('MAGIC_EDEN_API_KEY')

def setup_twitter():
    try:
        auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET)
        auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
        api = tweepy.API(auth)
        # Test the credentials
        api.verify_credentials()
        logging.info("Twitter authentication successful")
        return api
    except Exception as e:
        logging.error(f"Twitter authentication failed: {e}")
        return None

def get_sales():
    wait_time = 1  # Start with a 1 second wait time
    while True:
        try:
            headers = {
                "accept": "application/json",
                "Authorization": f"Bearer {API_KEY}",  # Include your API key here
                "User-Agent": "Mozilla/5.0"
            }
            
            response = requests.get(f"{BASE_API_URL}/sales", headers=headers, params={"collectionName": COLLECTION_NAME, "limit": 20})
            
            if response.status_code == 429:  # Rate limit exceeded
                logging.warning("Rate limit exceeded. Waiting before retrying...")
                time.sleep(wait_time)  # Wait for the current wait time
                wait_time = min(wait_time * 2, 60)  # Exponentially increase wait time, max 60 seconds
                continue  # Retry the request
            
            response.raise_for_status()  # Raise exception for bad status codes
            
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching sales: {e}")
            return None

def get_listings():
    wait_time = 1  # Start with a 1 second wait time
    while True:
        try:
            headers = {
                "accept": "application/json",
                "Authorization": f"Bearer {API_KEY}",  # Include your API key here
            "User-Agent": "Mozilla/5.0"
        }
        
        response = requests.get(f"{BASE_API_URL}/listings", headers=headers, params={"collectionName": COLLECTION_NAME, "type": "buyNow", "limit": 20})
        response.raise_for_status()  # Raise exception for bad status codes
        
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching listings: {e}")
        return None

def get_activities():
    try:
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {API_KEY}",
            "User-Agent": "Mozilla/5.0"
        }
        
        response = requests.get(f"{BASE_API_URL}/activities", headers=headers, params={"collectionName": COLLECTION_NAME, "limit": 20})
        response.raise_for_status()  # Raise exception for bad status codes
        
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching activities: {e}")
        return None

def format_tweet(sale):
    try:
        price_btc = float(sale.get('price', 0)) / 100000000
        inscription_id = sale.get('inscriptionId', 'Unknown')
        
        return (f"ALERT! New Fukuhedron Sale!\n"
                f"Price: {price_btc:.8f} BTC\n"
                f"View: https://ordinals.com/inscription/{inscription_id}")
    except Exception as e:
        logging.error(f"Error formatting tweet: {e}")
        return None

def main():
    # Check if environment variables are set
    if not all([TWITTER_API_KEY, TWITTER_API_SECRET, 
                TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET, 
                API_KEY]):
        logging.error("Missing API credentials!")
        return

    twitter_api = setup_twitter()
    if not twitter_api:
        logging.error("Failed to initialize Twitter API")
        return

    processed_sales = set()
    logging.info("Bot started! Monitoring Fukuhedrons sales...")
    
    while True:
        try:
            # You can choose which function to call based on your needs
            sales = get_sales()  # Fetch sales data
            # sales = get_listings()  # Uncomment to fetch listings
            # sales = get_activities()  # Uncomment to fetch activities
            
            if sales:
                for sale in sales:
                    sale_id = sale.get('signature')
                    
                    if sale_id and sale_id not in processed_sales:
                        tweet_text = format_tweet(sale)
                        if tweet_text:
                            try:
                                twitter_api.update_status(tweet_text)
                                logging.info(f"Tweeted: {tweet_text}")
                                processed_sales.add(sale_id)
                            except tweepy.TweepError as e:
                                logging.error(f"Error posting tweet: {e}")
            
            # Prevent processed_sales from growing too large
            if len(processed_sales) > 1000:
                processed_sales.clear()
                
            time.sleep(30)  # Wait 30 seconds between checks
            
        except Exception as e:
            logging.error(f"Error in main loop: {e}")
            time.sleep(60)  # Wait longer on error

if __name__ == "__main__":
    main()
