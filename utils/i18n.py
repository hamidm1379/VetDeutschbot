"""
Internationalization (i18n) system for the bot.
Supports dynamic language loading and easy addition of new languages.
"""
import json
import os
from pathlib import Path
from typing import Dict, Optional, List
from functools import lru_cache


class I18n:
    """Internationalization manager."""
    
    def __init__(self, locales_dir: str = "locales"):
        """
        Initialize i18n system.
        
        Args:
            locales_dir: Directory containing locale JSON files
        """
        self.locales_dir = Path(locales_dir)
        self._translations: Dict[str, Dict] = {}
        self._available_languages: List[Dict] = []
        self._default_language = "en"
        self._load_all_locales()
    
    def _load_all_locales(self):
        """Load all locale files from the locales directory."""
        if not self.locales_dir.exists():
            raise FileNotFoundError(f"Locales directory not found: {self.locales_dir}")
        
        for locale_file in self.locales_dir.glob("*.json"):
            try:
                with open(locale_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                lang_code = data.get('meta', {}).get('code', locale_file.stem)
                self._translations[lang_code] = data
                
                # Store language metadata
                meta = data.get('meta', {})
                self._available_languages.append({
                    'code': lang_code,
                    'name': meta.get('name', lang_code),
                    'native_name': meta.get('native_name', lang_code),
                    'rtl': meta.get('rtl', False)
                })
            except Exception as e:
                print(f"Error loading locale file {locale_file}: {e}")
        
        # Sort languages by code
        self._available_languages.sort(key=lambda x: x['code'])
        
        if not self._translations:
            raise ValueError("No locale files found!")
    
    def get_available_languages(self) -> List[Dict]:
        """Get list of available languages with metadata."""
        # Filter out English ('en') from the list
        return [lang for lang in self._available_languages if lang['code'] != 'en']
    
    def get_language_codes(self) -> List[str]:
        """Get list of available language codes."""
        return [lang['code'] for lang in self._available_languages]
    
    def is_rtl(self, language: str) -> bool:
        """Check if language is RTL."""
        lang_data = self._translations.get(language, {})
        return lang_data.get('meta', {}).get('rtl', False)
    
    @lru_cache(maxsize=128)
    def get_text(self, key: str, language: str = None, **kwargs) -> str:
        """
        Get translated text by key and language.
        
        Args:
            key: Translation key
            language: Language code (defaults to default_language)
            **kwargs: Format arguments for string formatting
        
        Returns:
            Translated text or key if not found
        """
        if language is None:
            language = self._default_language
        
        # Get translation for the language
        translations = self._translations.get(language, {})
        text = translations.get(key)
        
        # Fallback to default language if not found
        if text is None and language != self._default_language:
            translations = self._translations.get(self._default_language, {})
            text = translations.get(key)
        
        # Fallback to key if still not found
        if text is None:
            return key
        
        # Format with kwargs if provided
        if kwargs:
            try:
                return text.format(**kwargs)
            except (KeyError, ValueError):
                return text
        
        return text
    
    def format_text(self, key: str, language: str = None, **kwargs) -> str:
        """
        Get translated text and format it with provided arguments.
        
        Args:
            key: Translation key
            language: Language code
            **kwargs: Format arguments
        
        Returns:
            Formatted translated text
        """
        return self.get_text(key, language, **kwargs)
    
    def set_default_language(self, language: str):
        """Set default language."""
        if language in self._translations:
            self._default_language = language
        else:
            raise ValueError(f"Language '{language}' not available")
    
    def reload(self):
        """Reload all locale files (useful for development)."""
        self._translations.clear()
        self._available_languages.clear()
        self.get_text.cache_clear()
        self._load_all_locales()


# Global i18n instance
_i18n_instance: Optional[I18n] = None


def get_i18n() -> I18n:
    """Get global i18n instance."""
    global _i18n_instance
    if _i18n_instance is None:
        _i18n_instance = I18n()
    return _i18n_instance


def get_text(key: str, language: str = None, **kwargs) -> str:
    """Convenience function to get translated text."""
    return get_i18n().get_text(key, language, **kwargs)


def format_text(key: str, language: str = None, **kwargs) -> str:
    """Convenience function to format translated text."""
    return get_i18n().format_text(key, language, **kwargs)


def get_available_languages() -> List[Dict]:
    """Get list of available languages."""
    return get_i18n().get_available_languages()


def is_rtl(language: str) -> bool:
    """Check if language is RTL."""
    return get_i18n().is_rtl(language)
