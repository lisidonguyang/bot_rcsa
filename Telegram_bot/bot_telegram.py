import time
import requests
import traceback
import json
import os
import inspect
import logging
from json import load
from urllib.parse import quote
from typing import Optional, Dict, Any
from dataclasses import dataclass
from pathlib import Path


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@dataclass
class TelegramConfig:
    """Class to hold Telegram configuration"""
    bot_token: str
    bot_chatID: str

class TelegramBot:
    def __init__(self, config_path: Optional[str] = None):
        """Initialize TelegramBot with configuration"""
        self.config = self._load_config(config_path)
        self.base_url = f'https://api.telegram.org/bot{self.config.bot_token}'

    def _load_config(self, config_path: Optional[str] = None) -> TelegramConfig:
        """Load configuration from file"""
        try:
            if config_path is None:
                current_file = inspect.getframeinfo(inspect.currentframe()).filename
                config_path = os.path.join(os.path.dirname(os.path.abspath(current_file)), 'config.json')

            with open(config_path, 'r') as f:
                config = load(f)

            bot_token = config['telegram']['bot_token']
            bot_chatID = str(config['telegram']['bot_chatID'])

            if bot_token == "BOTTOKEN":
                raise ValueError("Bot token not configured in config.json")

            return TelegramConfig(bot_token=bot_token, bot_chatID=bot_chatID)

        except FileNotFoundError:
            logging.error("Configuration file not found")
            raise
        except json.JSONDecodeError:
            logging.error("Invalid JSON in configuration file")
            raise
        except Exception as e:
            logging.error(f"Error loading configuration: {str(e)}")
            raise

    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict:
        """Make request to Telegram API"""
        try:
            url = f"{self.base_url}/{endpoint}"
            params['chat_id'] = self.config.bot_chatID
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logging.error(f"Telegram API request failed: {str(e)}")
            raise

    def send_message(self, message: str, parse_mode: str = 'Markdown') -> Dict:
        """Send text message"""
        return self._make_request('sendMessage', {
            'text': message,
            'parse_mode': parse_mode
        })

    def send_match_notification(self, home: str, away: str) -> Dict:
        """Send formatted match notification"""
        message = (
            f"🆕 *New Match Added!*\n"
            f"🏠 Home: {home}\n"
            f"🏃 Away: {away}\n"
            f"⏰ Added: {time.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        return self.send_message(message)

    def send_image(self, image_url: str, caption: Optional[str] = None) -> Dict:
        """Send image with optional caption"""
        params = {'photo': image_url}
        if caption:
            params['caption'] = caption
            params['parse_mode'] = 'Markdown'
        return self._make_request('sendPhoto', params)

    def delete_message(self, message_id: int) -> Dict:
        """Delete a message"""
        return self._make_request('deleteMessage', {
            'message_id': message_id
        })

    def send_health_check(self) -> Dict:
        """Send health check message"""
        message = (
            f"🤖 *Bot Health Check*\n"
            f"✅ Status: Active\n"
            f"⏰ Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"📡 Service: Match Tracker"
        )
        return self.send_message(message)

def create_telegram_bot() -> TelegramBot:
    """Factory function to create TelegramBot instance"""
    try:
        return TelegramBot()
    except Exception as e:
        logging.error(f"Failed to create TelegramBot: {str(e)}")
        raise

# For backwards compatibility
_bot_instance = None

def get_bot_instance() -> TelegramBot:
    """Get or create singleton bot instance"""
    global _bot_instance
    if _bot_instance is None:
        _bot_instance = create_telegram_bot()
    return _bot_instance

# Legacy support functions
def telegram_bot_sendtext(bot_message: str, only_to_admin: bool = True) -> Dict:
    """Legacy support function for sending text messages"""
    return get_bot_instance().send_message(bot_message)

def telegram_bot_sendimage(image_url: str, image_caption: Optional[str] = None) -> Dict:
    """Legacy support function for sending images"""
    return get_bot_instance().send_image(image_url, image_caption)

def telegram_bot_delete_message(message_id: int) -> Dict:
    """Legacy support function for deleting messages"""
    return get_bot_instance().delete_message(message_id)

def still_alive() -> Dict:
    """Legacy support function for health check"""
    return get_bot_instance().send_health_check()