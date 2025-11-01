"""Generate images using GenAI APIs (OpenAI DALL-E)."""
import os
from pathlib import Path
from typing import Optional
from PIL import Image
import requests
from io import BytesIO
from openai import OpenAI


class ImageGenerator:
    """Handles AI-powered image generation."""
    
    def __init__(self):
        """Initialize image generator with API key from environment."""
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY in .env file."
            )
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = "dall-e-3"
        self.size = "1024x1024"
        self.quality = "standard"
    
    def build_prompt(
        self,
        product_name: str,
        product_description: str,
        target_audience: str,
        brand_color: Optional[str] = None
    ) -> str:
        """
        Build an optimized prompt for image generation.
        
        Args:
            product_name: Name of the product
            product_description: Product description
            target_audience: Target audience description
            brand_color: Primary brand color (hex)
            
        Returns:
            Optimized prompt string
        """
        prompt_parts = [
            f"Professional product photography of {product_name}.",
            f"Product details: {product_description}.",
            f"Style: Clean, modern, appealing to {target_audience}.",
            "High quality, well-lit, studio setting.",
        ]
        
        if brand_color:
            prompt_parts.append(f"Incorporate {brand_color} color accent.")
        
        prompt_parts.append("Commercial photography, 4K quality.")
        
        return " ".join(prompt_parts)
    
    def generate(
        self,
        product_name: str,
        product_description: str,
        target_audience: str,
        brand_color: Optional[str] = None
    ) -> tuple[Image.Image, str]:
        """
        Generate a product image using DALL-E.
        
        Args:
            product_name: Name of the product
            product_description: Product description
            target_audience: Target audience description
            brand_color: Primary brand color (hex)
            
        Returns:
            Tuple of (PIL Image, prompt used)
            
        Raises:
            Exception: If generation fails
        """
        prompt = self.build_prompt(
            product_name,
            product_description,
            target_audience,
            brand_color
        )
        
        try:
            response = self.client.images.generate(
                model=self.model,
                prompt=prompt,
                size=self.size,
                quality=self.quality,
                n=1
            )
            
            # Download the generated image
            image_url = response.data[0].url
            image_response = requests.get(image_url)
            image_response.raise_for_status()
            
            # Convert to PIL Image
            image = Image.open(BytesIO(image_response.content))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            return image, prompt
            
        except Exception as e:
            raise Exception(f"Failed to generate image for {product_name}: {e}")
    
    def generate_with_retry(
        self,
        product_name: str,
        product_description: str,
        target_audience: str,
        brand_color: Optional[str] = None,
        max_retries: int = 3
    ) -> tuple[Image.Image, str]:
        """
        Generate image with retry logic.
        
        Args:
            product_name: Name of the product
            product_description: Product description
            target_audience: Target audience description
            brand_color: Primary brand color (hex)
            max_retries: Maximum number of retry attempts
            
        Returns:
            Tuple of (PIL Image, prompt used)
            
        Raises:
            Exception: If all retries fail
        """
        last_error = None
        
        for attempt in range(max_retries):
            try:
                return self.generate(
                    product_name,
                    product_description,
                    target_audience,
                    brand_color
                )
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    print(f"  Retry {attempt + 1}/{max_retries - 1}...")
                    continue
        
        raise Exception(f"Failed after {max_retries} attempts: {last_error}")
