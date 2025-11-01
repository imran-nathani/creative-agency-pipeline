"""Parse and validate campaign briefs."""
import yaml
from pathlib import Path
from typing import Union
from .models import CampaignBrief


class BriefParser:
    """Handles parsing and validation of campaign briefs."""
    
    @staticmethod
    def parse(brief_path: Union[str, Path]) -> CampaignBrief:
        """
        Parse a campaign brief from YAML file.
        
        Args:
            brief_path: Path to the brief YAML file
            
        Returns:
            Validated CampaignBrief object
            
        Raises:
            FileNotFoundError: If brief file doesn't exist
            ValueError: If brief format is invalid
        """
        brief_path = Path(brief_path)
        
        if not brief_path.exists():
            raise FileNotFoundError(f"Brief file not found: {brief_path}")
        
        with open(brief_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        try:
            brief = CampaignBrief(**data)
            return brief
        except Exception as e:
            raise ValueError(f"Invalid brief format: {e}")
    
    @staticmethod
    def validate_brief(brief: CampaignBrief) -> tuple[bool, list[str]]:
        """
        Validate campaign brief for completeness.
        
        Args:
            brief: CampaignBrief object to validate
            
        Returns:
            Tuple of (is_valid, list_of_warnings)
        """
        warnings = []
        
        # Check minimum products
        if len(brief.products) < 2:
            warnings.append(f"Brief requires at least 2 products, found {len(brief.products)}")
        
        # Check for missing hero images
        missing_images = [p.name for p in brief.products if not p.hero_image]
        if missing_images:
            warnings.append(f"Products without hero images (will generate): {', '.join(missing_images)}")
        
        # Check brand elements
        if not brief.brand_elements:
            warnings.append("No brand elements specified")
        
        is_valid = len(brief.products) >= 2
        return is_valid, warnings
