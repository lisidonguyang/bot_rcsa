from Web_scraper.web_scraper import web_scraper
from Telegram_bot.bot_telegram import get_bot_instance
import duckdb
import logging
from typing import List, Tuple
from contextlib import contextmanager
import time
import os

DB_PATH = os.getenv('DB_PATH', 'file.db')


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = duckdb.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()

def init_database():
    """Initialize the database and create the matches table if it doesn't exist"""
    with get_db_connection() as conn:
        #remove database matches in duckdb if it exists
        conn.sql("CREATE TABLE IF NOT EXISTS matches(home VARCHAR, away VARCHAR)")

def get_new_matches(current_matches: List[Tuple[str, str]], stored_matches: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
    """
    Compare current matches with stored matches to find new ones
    Returns list of new matches as (home, away) tuples
    """
    return [match for match in current_matches if match not in stored_matches]

def notify_new_matches(new_matches):
    """Send notifications for new matches"""
    bot = get_bot_instance()
    for home, away in new_matches:
        try:
            bot.send_match_notification(home, away)
            logging.info(f"Notification sent for match: {home} vs {away}")
        except Exception as e:
            logging.error(f"Failed to send notification: {str(e)}")

def main():
    #try:
        # Initialize database
        init_database()
        
        # Get current matches from web scraper
        current_df = web_scraper()
        
        with get_db_connection() as conn:
            # Get stored matches
            stored_df = conn.table("matches").df()
            
            # Convert DataFrames to list of tuples for easier comparison
            current_matches = list(zip(current_df['home'], current_df['away']))
            stored_matches = list(zip(stored_df['home'], stored_df['away']))
            
            # Find new matches
            new_matches = get_new_matches(current_matches, stored_matches)
            
            if new_matches:
                # Insert new matches into database
                conn.register("current_df", current_df)
                conn.sql("""
                    INSERT INTO matches 
                    SELECT * FROM current_df 
                    WHERE NOT EXISTS (
                        SELECT 1 FROM matches 
                        WHERE matches.home = current_df.home 
                        AND matches.away = current_df.away
                    )
                """)
                
                # Notify about new matches
                notify_new_matches(new_matches)
            else:
                logging.info("No new matches found")

    #except Exception as e:
        #logging.error(f"An error occurred: {str(e)}")
        #telegram_bot_sendtext(f"Error in match scraper: {str(e)}")

if __name__ == "__main__":
    while True:
        main()
        time.sleep(60)