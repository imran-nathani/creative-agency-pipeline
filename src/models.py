"""Data models for campaign briefs and configuration."""
from typing import Optional, List
from pydantic import BaseModel, Field


class Product(BaseModel):
    """Product information from campaign brief."""
    id: str
    name: str
    description: str
    hero_image: Optional[str] = None


class TargetMarket(BaseModel):
    """Target market information."""
    region: str
    language: str = "en-US"


class BrandElements(BaseModel):
    """Brand identity elements."""
    logo: Optional[str] = None
    primary_color: str = "#000000"
    font: str = "Arial"


class CampaignBrief(BaseModel):
    """Complete campaign brief structure."""
    campaign_id: str
    products: List[Product]
    target_market: TargetMarket
    target_audience: str
    campaign_message: str
    brand_elements: Optional[BrandElements] = None


class AspectRatio(BaseModel):
    """Aspect ratio configuration."""
    name: str
    ratio: List[int]
    width: int
    height: int


class GeneratedAsset(BaseModel):
    """Metadata for a generated asset."""
    product_id: str
    product_name: str
    aspect_ratio: str
    file_path: str
    source: str  # "existing" or "generated"
    prompt_used: Optional[str] = None
