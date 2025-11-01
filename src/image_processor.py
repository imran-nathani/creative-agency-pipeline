"""Process images: resize, crop, and add text overlays."""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from typing import Optional, Tuple
import textwrap


class ImageProcessor:
    """Handles image processing operations."""
    
    def __init__(self):
        """Initialize image processor."""
        pass
    
    def smart_crop(
        self,
        image: Image.Image,
        target_width: int,
        target_height: int
    ) -> Image.Image:
        """
        Crop image to target dimensions using center crop.
        
        Args:
            image: Source PIL Image
            target_width: Target width in pixels
            target_height: Target height in pixels
            
        Returns:
            Cropped PIL Image
        """
        # Calculate aspect ratios
        source_ratio = image.width / image.height
        target_ratio = target_width / target_height
        
        if source_ratio > target_ratio:
            # Image is wider than target - crop width
            new_width = int(image.height * target_ratio)
            left = (image.width - new_width) // 2
            image = image.crop((left, 0, left + new_width, image.height))
        else:
            # Image is taller than target - crop height
            new_height = int(image.width / target_ratio)
            top = (image.height - new_height) // 2
            image = image.crop((0, top, image.width, top + new_height))
        
        # Resize to exact dimensions
        return image.resize((target_width, target_height), Image.Resampling.LANCZOS)
    
    def resize_for_aspect_ratio(
        self,
        image: Image.Image,
        width: int,
        height: int
    ) -> Image.Image:
        """
        Resize image to specific dimensions with smart cropping.
        
        Args:
            image: Source PIL Image
            width: Target width
            height: Target height
            
        Returns:
            Resized PIL Image
        """
        return self.smart_crop(image, width, height)
    
    def add_text_overlay(
        self,
        image: Image.Image,
        text: str,
        position: str = "bottom",
        font_size: int = 72,
        text_color: str = "#FFFFFF",
        stroke_color: str = "#000000",
        stroke_width: int = 3,
        padding: int = 60
    ) -> Image.Image:
        """
        Add text overlay to image.
        
        Args:
            image: PIL Image to add text to
            text: Text to overlay
            position: Position of text ("top", "center", "bottom")
            font_size: Font size in points
            text_color: Text color (hex)
            stroke_color: Stroke/outline color (hex)
            stroke_width: Width of text stroke
            padding: Padding from edges
            
        Returns:
            Image with text overlay
        """
        # Create a copy to avoid modifying original
        img = image.copy()
        draw = ImageDraw.Draw(img)
        
        # Try to load a nice font, fallback to default
        try:
            # Try common font locations
            font_paths = [
                "C:/Windows/Fonts/arial.ttf",
                "C:/Windows/Fonts/arialbd.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                "/System/Library/Fonts/Helvetica.ttc"
            ]
            font = None
            for font_path in font_paths:
                if Path(font_path).exists():
                    font = ImageFont.truetype(font_path, font_size)
                    break
            if font is None:
                font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()
        
        # Wrap text to fit image width
        max_width = img.width - (padding * 2)
        wrapped_text = self._wrap_text(text, font, max_width, draw)
        
        # Calculate text bounding box
        bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Calculate position
        x = (img.width - text_width) // 2
        
        if position == "top":
            y = padding
        elif position == "center":
            y = (img.height - text_height) // 2
        else:  # bottom
            y = img.height - text_height - padding
        
        # Draw text with stroke for better visibility
        draw.multiline_text(
            (x, y),
            wrapped_text,
            font=font,
            fill=text_color,
            stroke_width=stroke_width,
            stroke_fill=stroke_color,
            align="center"
        )
        
        return img
    
    def _wrap_text(
        self,
        text: str,
        font: ImageFont.FreeTypeFont,
        max_width: int,
        draw: ImageDraw.ImageDraw
    ) -> str:
        """
        Wrap text to fit within max width.
        
        Args:
            text: Text to wrap
            font: Font to use
            max_width: Maximum width in pixels
            draw: ImageDraw object for measuring
            
        Returns:
            Wrapped text with newlines
        """
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            width = bbox[2] - bbox[0]
            
            if width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return '\n'.join(lines)
    
    def add_logo(
        self,
        image: Image.Image,
        logo_path: Path,
        position: str = "top-right",
        size: int = 150,
        padding: int = 40
    ) -> Image.Image:
        """
        Add logo to image.
        
        Args:
            image: PIL Image to add logo to
            logo_path: Path to logo file
            position: Position of logo ("top-left", "top-right", "bottom-left", "bottom-right")
            size: Maximum size of logo (maintains aspect ratio)
            padding: Padding from edges
            
        Returns:
            Image with logo
        """
        if not logo_path.exists():
            return image
        
        # Create a copy
        img = image.copy()
        
        # Load and resize logo
        logo = Image.open(logo_path)
        
        # Convert logo to RGBA if it isn't already
        if logo.mode != 'RGBA':
            logo = logo.convert('RGBA')
        
        # Resize logo maintaining aspect ratio
        logo.thumbnail((size, size), Image.Resampling.LANCZOS)
        
        # Calculate position
        if position == "top-left":
            x, y = padding, padding
        elif position == "top-right":
            x = img.width - logo.width - padding
            y = padding
        elif position == "bottom-left":
            x = padding
            y = img.height - logo.height - padding
        else:  # bottom-right
            x = img.width - logo.width - padding
            y = img.height - logo.height - padding
        
        # Paste logo with transparency
        img.paste(logo, (x, y), logo)
        
        return img
