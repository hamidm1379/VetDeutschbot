"""
Helper functions for admin handlers (i18n-ready).
"""
from typing import Dict, List
from utils.i18n import get_available_languages, get_text


def get_language_collection_states() -> Dict:
    """
    Generate conversation states for collecting multilingual content.
    Returns a dictionary mapping state names to state values.
    """
    languages = get_available_languages()
    states = {}
    state_counter = 100  # Start from 100 to avoid conflicts
    
    # Generate states for collecting titles
    for lang in languages:
        states[f'ADD_STEP_TITLE_{lang["code"].upper()}'] = state_counter
        state_counter += 1
    
    # Generate states for collecting descriptions
    for lang in languages:
        states[f'ADD_STEP_DESC_{lang["code"].upper()}'] = state_counter
        state_counter += 1
    
    # Generate states for editing
    for lang in languages:
        states[f'EDIT_STEP_TITLE_{lang["code"].upper()}'] = state_counter
        state_counter += 1
    
    for lang in languages:
        states[f'EDIT_STEP_DESC_{lang["code"].upper()}'] = state_counter
        state_counter += 1
    
    # Question states
    for lang in languages:
        states[f'ADD_QUESTION_{lang["code"].upper()}'] = state_counter
        state_counter += 1
    
    for lang in languages:
        states[f'EDIT_QUESTION_{lang["code"].upper()}'] = state_counter
        state_counter += 1
    
    return states


def collect_multilingual_content(context, field_prefix: str, languages: List[Dict]) -> Dict[str, str]:
    """
    Collect multilingual content from context.user_data.
    
    Args:
        context: Context object
        field_prefix: Prefix for field names (e.g., 'new_step_title')
        languages: List of language dictionaries
    
    Returns:
        Dictionary mapping language codes to content
    """
    content = {}
    for lang in languages:
        code = lang['code']
        key = f'{field_prefix}_{code}'
        value = context.user_data.get(key)
        if value:
            content[code] = value
    return content


def get_next_language_to_collect(context, field_prefix: str, languages: List[Dict]) -> Dict:
    """
    Get the next language that needs content collection.
    
    Returns:
        Language dict or None if all collected
    """
    collected = set()
    for lang in languages:
        code = lang['code']
        key = f'{field_prefix}_{code}'
        if context.user_data.get(key):
            collected.add(code)
    
    for lang in languages:
        if lang['code'] not in collected:
            return lang
    
    return None
