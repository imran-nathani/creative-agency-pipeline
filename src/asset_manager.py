"""Manage campaign assets - check for existing files and handle storage."""
from pathlib import Path
from typing import Optional
import shutil
from PIL import Image


class AssetManager:
    """Handles asset discovery and storage operations."""
    
    def __init__(self, campaign_root: Path):
        """
        Initialize asset manager.
        
        Args:
            campaign_root: Root directory of the campaign
        """
        self.campaign_root = Path(campaign_root)
        self.assets_dir = self.campaign_root / "assets"
        self.output_dir = self.campaign_root / "output"
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def find_asset(self, asset_path: Optional[str]) -> Optional[Path]:
        """
        Find an asset file, checking multiple possible locations.
        
        Args:
            asset_path: Relative path from brief (e.g., "assets/logo.png")
            
        Returns:
            Absolute path to asset if found, None otherwise
        """
        if not asset_path:
            return None
        
        # Try relative to campaign root
        full_path = self.campaign_root / asset_path
        if full_path.exists():
            return full_path
        
        # Try in assets directory
        asset_name = Path(asset_path).name
        assets_path = self.assets_dir / asset_name
        if assets_path.exists():
            return assets_path
        
        return None
    
    def load_image(self, image_path: Path) -> Image.Image:
        """
        Load an image file.
        
        Args:
            image_path: Path to image file
            
        Returns:
            PIL Image object
            
        Raises:
            FileNotFoundError: If image doesn't exist
            ValueError: If file is not a valid image
        """
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        try:
            img = Image.open(image_path)
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            return img
        except Exception as e:
            raise ValueError(f"Failed to load image {image_path}: {e}")
    
    def save_output(
        self,
        image: Image.Image,
        product_id: str,
        aspect_ratio_name: str,
        filename: str = "campaign_post.png"
    ) -> Path:
        """
        Save generated image to organized output directory.
        
        Args:
            image: PIL Image to save
            product_id: Product identifier
            aspect_ratio_name: Name of aspect ratio (e.g., "square", "story")
            filename: Output filename
            
        Returns:
            Path where image was saved
        """
        # Create organized directory structure
        output_path = self.output_dir / product_id / aspect_ratio_name
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save image
        file_path = output_path / filename
        image.save(file_path, format='PNG', quality=95)
        
        return file_path
    
    def get_output_structure(self) -> dict:
        """
        Get the current output directory structure.
        
        Returns:
            Dictionary mapping products to their generated assets
        """
        structure = {}
        
        if not self.output_dir.exists():
            return structure
        
        for product_dir in self.output_dir.iterdir():
            if product_dir.is_dir():
                structure[product_dir.name] = []
                for ratio_dir in product_dir.iterdir():
                    if ratio_dir.is_dir():
                        files = list(ratio_dir.glob("*.png"))
                        structure[product_dir.name].extend([
                            f"{ratio_dir.name}/{f.name}" for f in files
                        ])
        
        return structure
