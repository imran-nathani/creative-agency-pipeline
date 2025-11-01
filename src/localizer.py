"""Localization support for multi-language campaigns."""
from typing import Optional
from deep_translator import GoogleTranslator


class Localizer:
    """Handles text translation and language-specific formatting."""
    
    def __init__(self):
        """Initialize localizer with translation service."""
        self.font_map = self._get_font_map()
    
    def _get_font_map(self) -> dict:
        """Map languages to appropriate fonts (English, Spanish, Japanese only)."""
        return {
            'en': 'Arial',
            'es': 'Arial',
            'ja': 'Noto Sans JP',
        }
    
    def translate_text(
        self,
        text: str,
        target_language: str,
        source_language: str = 'en'
    ) -> str:
        """
        Translate text to target language.
        
        Args:
            text: Text to translate
            target_language: Target language code (ISO 639-1)
            source_language: Source language code (default: 'en')
            
        Returns:
            Translated text
        """
        # Skip translation if target is same as source
        if target_language == source_language:
            return text
        
        try:
            translator = GoogleTranslator(source=source_language, target=target_language)
            result = translator.translate(text)
            return result
        except Exception as e:
            print(f"Warning: Translation failed: {e}")
            print(f"Using original text: {text}")
            return text
    
    def get_font_for_language(self, language: str) -> str:
        """
        Get appropriate font for language (English, Spanish, Japanese only).
        
        Args:
            language: Language code (ISO 639-1)
            
        Returns:
            Font name (defaults to Arial for unsupported languages)
        """
        return self.font_map.get(language.lower(), 'Arial')
    
    def localize_message(
        self,
        message: str,
        target_language: str,
        preserve_terms: Optional[list[str]] = None
    ) -> str:
        """
        Localize campaign message with term preservation.
        
        Args:
            message: Original message
            target_language: Target language code
            preserve_terms: Terms to not translate (e.g., brand names)
            
        Returns:
            Localized message
        """
        if target_language == 'en':
            return message
        
        # Simple implementation - translate everything
        # For production, would implement term preservation
        translated = self.translate_text(message, target_language)
        
        # TODO: Implement term preservation if needed
        # Replace preserved terms back into translated text
        
        return translated
