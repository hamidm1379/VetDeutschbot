"""
Helper utility functions.
"""
import json
import logging
from typing import List, Dict, Any
from telegram.error import TimedOut, NetworkError, BadRequest
from models import User
from config import Config

logger = logging.getLogger(__name__)


def is_admin(telegram_id: int) -> bool:
    """Check if user is admin."""
    return Config.is_admin(telegram_id)


def get_user_language(telegram_id: int) -> str:
    """Get user's language preference."""
    user = User.get_or_create(telegram_id)
    return user.get('language', 'fa') or 'fa'


def parse_options(options_text: str) -> List[str]:
    """Parse options from text (one per line)."""
    options = [opt.strip() for opt in options_text.split('\n') if opt.strip()]
    return options if len(options) >= 2 else []


def validate_correct_option(correct_option_str: str, total_options: int) -> int:
    """Validate and convert correct option number."""
    try:
        option_num = int(correct_option_str.strip())
        if 1 <= option_num <= total_options:
            return option_num - 1  # Convert to 0-based index
    except ValueError:
        pass
    return -1


def calculate_exam_score(answers: List[int], correct_answers: List[int]) -> float:
    """Calculate exam score percentage."""
    if not answers or not correct_answers:
        return 0.0
    
    correct = sum(1 for a, c in zip(answers, correct_answers) if a == c)
    return (correct / len(correct_answers)) * 100.0


async def safe_answer_callback(query, text: str = None, show_alert: bool = False):
    """
    Safely answer a callback query with timeout error handling.
    
    This function wraps query.answer() with retry logic and error handling
    to prevent crashes from network timeouts.
    
    Args:
        query: The callback query object
        text: Optional text to show in the answer
        show_alert: Whether to show an alert or a toast notification
    """
    try:
        await query.answer(text=text, show_alert=show_alert)
    except (TimedOut, NetworkError) as e:
        logger.warning(f"Timeout/Network error while answering callback query: {e}")
        # Try once more with a shorter timeout expectation
        try:
            await query.answer(text=text, show_alert=show_alert)
        except (TimedOut, NetworkError):
            # If it still fails, log but don't crash - the callback was likely processed
            logger.error(f"Failed to answer callback query after retry: {query.data}")
    except Exception as e:
        logger.error(f"Unexpected error while answering callback query: {e}", exc_info=True)


async def safe_reply_text(message, text: str, reply_markup=None, parse_mode=None, **kwargs):
    """
    Safely reply to a message with comprehensive error handling.
    
    This function wraps message.reply_text() with error handling for common issues:
    - Message too long
    - Invalid formatting
    - Network timeouts
    - Bad requests
    
    Args:
        message: Message object to reply to
        text: Text to send
        reply_markup: Optional InlineKeyboardMarkup
        parse_mode: Optional parse mode ('HTML', 'Markdown', etc.)
        **kwargs: Additional arguments to pass to reply_text
    
    Returns:
        Message object if successful, None otherwise
    """
    try:
        # Truncate text if too long (Telegram limit is 4096 characters)
        if len(text) > 4096:
            logger.warning(f"Message text too long ({len(text)} chars), truncating to 4096")
            text = text[:4093] + "..."
        
        return await message.reply_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
            **kwargs
        )
    except BadRequest as e:
        error_message = str(e).lower()
        if "message is too long" in error_message:
            # Shouldn't happen due to truncation, but handle just in case
            logger.error(f"Message still too long after truncation: {e}")
            return None
        else:
            # Other BadRequest errors (invalid HTML, etc.)
            logger.error(f"BadRequest error while replying to message: {e}")
            return None
    except (TimedOut, NetworkError) as e:
        logger.warning(f"Timeout/Network error while replying to message: {e}")
        # Try once more
        try:
            return await message.reply_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode,
                **kwargs
            )
        except (TimedOut, NetworkError):
            logger.error(f"Failed to reply to message after retry")
            return None
    except Exception as e:
        logger.error(f"Unexpected error while replying to message: {e}", exc_info=True)
        return None


async def safe_edit_message_text(query_or_message, text: str, reply_markup=None, parse_mode=None, **kwargs):
    """
    Safely edit message text with comprehensive error handling.
    
    This function wraps edit_message_text() with error handling for common issues:
    - Message not modified (same content)
    - Message too long
    - Invalid formatting
    - Network timeouts
    - Message deleted
    
    Args:
        query_or_message: CallbackQuery or Message object
        text: Text to set
        reply_markup: Optional InlineKeyboardMarkup
        parse_mode: Optional parse mode ('HTML', 'Markdown', etc.)
        **kwargs: Additional arguments to pass to edit_message_text
    
    Returns:
        Message object if successful, None otherwise
    """
    try:
        # Truncate text if too long (Telegram limit is 4096 characters)
        if len(text) > 4096:
            logger.warning(f"Message text too long ({len(text)} chars), truncating to 4096")
            text = text[:4093] + "..."
        
        return await query_or_message.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
            **kwargs
        )
    except BadRequest as e:
        error_message = str(e).lower()
        if "message is not modified" in error_message:
            # Message hasn't changed - this is not a critical error
            logger.debug(f"Message not modified (same content): {query_or_message.data if hasattr(query_or_message, 'data') else 'N/A'}")
            return None
        elif "message to edit not found" in error_message or "message can't be edited" in error_message:
            # Message was deleted or can't be edited
            logger.warning(f"Message cannot be edited (may have been deleted): {e}")
            return None
        elif "message is too long" in error_message:
            # Shouldn't happen due to truncation, but handle just in case
            logger.error(f"Message still too long after truncation: {e}")
            return None
        else:
            # Other BadRequest errors (invalid HTML, etc.)
            logger.error(f"BadRequest error while editing message: {e}")
            return None
    except (TimedOut, NetworkError) as e:
        logger.warning(f"Timeout/Network error while editing message: {e}")
        # Try once more
        try:
            return await query_or_message.edit_message_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode,
                **kwargs
            )
        except (TimedOut, NetworkError):
            logger.error(f"Failed to edit message after retry")
            return None
    except Exception as e:
        logger.error(f"Unexpected error while editing message: {e}", exc_info=True)
        return None
