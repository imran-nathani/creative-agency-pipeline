"""Brand compliance checking for generated assets."""
from pathlib import Path
from typing import Optional
from PIL import Image
import colorsys


class ComplianceResult:
    """Result of a compliance check."""
    
    def __init__(
        self,
        check_name: str,
        passed: bool,
        score: float,
        message: str,
        details: Optional[dict] = None
    ):
        self.check_name = check_name
        self.passed = passed
        self.score = score  # 0-100
        self.message = message
        self.details = details or {}


class BrandComplianceChecker:
    """Performs brand compliance checks on generated images."""
    
    def __init__(self, brand_color: Optional[str] = None, logo_path: Optional[Path] = None):
        """
        Initialize compliance checker.
        
        Args:
            brand_color: Primary brand color (hex format)
            logo_path: Path to brand logo
        """
        self.brand_color = brand_color
        self.logo_path = logo_path
    
    def check_color_presence(self, image: Image.Image) -> ComplianceResult:
        """
        Check if brand color is present in image.
        
        Args:
            image: PIL Image to check
            
        Returns:
            ComplianceResult
        """
        if not self.brand_color:
            return ComplianceResult(
                "color_presence",
                True,
                100.0,
                "No brand color specified - skipped"
            )
        
        try:
            # Convert brand color to RGB
            brand_rgb = self._hex_to_rgb(self.brand_color)
            
            # Sample image colors
            image_small = image.resize((100, 100))
            pixels = list(image_small.getdata())
            
            # Check if brand color (or similar) is present
            tolerance = 30  # RGB tolerance
            color_found = False
            
            for pixel in pixels:
                if len(pixel) >= 3:
                    r, g, b = pixel[:3]
                    if (abs(r - brand_rgb[0]) < tolerance and
                        abs(g - brand_rgb[1]) < tolerance and
                        abs(b - brand_rgb[2]) < tolerance):
                        color_found = True
                        break
            
            if color_found:
                return ComplianceResult(
                    "color_presence",
                    True,
                    100.0,
                    f"Brand color {self.brand_color} detected"
                )
            else:
                return ComplianceResult(
                    "color_presence",
                    False,
                    50.0,
                    f"Brand color {self.brand_color} not prominently featured",
                    {"brand_color": self.brand_color}
                )
        
        except Exception as e:
            return ComplianceResult(
                "color_presence",
                False,
                0.0,
                f"Color check failed: {e}"
            )
    
    def run_brand_checks(self, image: Image.Image) -> dict:
        """
        Run brand compliance check (color presence only).
        
        Args:
            image: PIL Image to check
            
        Returns:
            Dictionary with check results
        """
        # Only check color presence
        color_check = self.check_color_presence(image)
        
        return {
            "overall_passed": color_check.passed,
            "overall_score": round(color_check.score, 1),
            "checks": {
                "color_presence": {
                    "passed": color_check.passed,
                    "score": color_check.score,
                    "message": color_check.message,
                    "details": color_check.details
                }
            }
        }
    
    def _hex_to_rgb(self, hex_color: str) -> tuple:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
