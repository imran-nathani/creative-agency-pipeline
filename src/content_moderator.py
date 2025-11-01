"""Content moderation for campaign messages and AI prompts."""
from typing import Optional


class ModerationResult:
    """Result of content moderation check."""
    
    def __init__(self, flagged: bool, categories: dict, prohibited_terms: list[str] = None):
        self.flagged = flagged
        self.categories = categories
        self.prohibited_terms = prohibited_terms or []
    
    def is_safe(self) -> bool:
        """Check if content passed all moderation checks."""
        return not self.flagged and len(self.prohibited_terms) == 0


class ContentModerator:
    """Handles content moderation using OpenAI API and keyword filtering."""
    
    def __init__(self, prohibited_terms: Optional[list[str]] = None):
        """
        Initialize content moderator.
        
        Args:
            prohibited_terms: List of prohibited keywords (optional)
        """
        self.prohibited_terms = prohibited_terms or self._load_default_terms()
    
    def _load_default_terms(self) -> list[str]:
        """Load default prohibited terms."""
        # Add industry-specific terms as needed
        return [
            "guaranteed",
            "miracle",
            "cure",
            # Add more terms based on legal/compliance requirements
        ]
    
    def moderate_text(self, text: str) -> ModerationResult:
        """
        Check text using keyword filtering.
        
        Args:
            text: Text to moderate
            
        Returns:
            ModerationResult with flagged status and details
        """
        # Check for prohibited terms
        found_terms = self.check_prohibited_terms(text)
        
        # AI moderation stub
        flagged = self._ai_moderation_check(text)
        
        return ModerationResult(
            flagged=flagged,
            categories={},
            prohibited_terms=found_terms
        )
    
    def _ai_moderation_check(self, text: str) -> bool:
        """
        AI-powered content moderation (stub for future enhancement).
        
        TODO: Future Enhancement - Integrate OpenAI Moderation API
        - Use OpenAI Moderation API for advanced content safety checks
        - Detect harmful content categories (hate, violence, sexual, etc.)
        - Provide detailed category-level flagging
        
        Example implementation:
            response = self.client.moderations.create(input=text)
            return response.results[0].flagged
        
        Args:
            text: Text to check
            
        Returns:
            False (not implemented - always passes)
        """
        # Stub: Always return False (no AI moderation yet)
        return False
    
    def check_prohibited_terms(self, text: str) -> list[str]:
        """
        Check for prohibited keywords.
        
        Args:
            text: Text to check
            
        Returns:
            List of found prohibited terms
        """
        found_terms = []
        text_lower = text.lower()
        
        for term in self.prohibited_terms:
            if term.lower() in text_lower:
                found_terms.append(term)
        
        return found_terms
    
    def moderate_campaign_message(self, message: str, strict: bool = False) -> bool:
        """
        Moderate campaign message.
        
        Args:
            message: Campaign message to check
            strict: If True, raise exception on failure
            
        Returns:
            True if safe, False otherwise
            
        Raises:
            ValueError: If strict=True and prohibited terms found
        """
        result = self.moderate_text(message)
        
        if not result.is_safe():
            error_msg = f"Campaign message failed moderation:\n"
            error_msg += f"  - Prohibited terms found: {', '.join(result.prohibited_terms)}\n"
            
            if strict:
                raise ValueError(error_msg)
            else:
                print(f"Warning: {error_msg}")
                return False
        
        return True
