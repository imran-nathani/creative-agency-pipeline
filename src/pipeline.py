"""Main pipeline orchestrator for creative automation."""
from pathlib import Path
from typing import List, Optional
import yaml
from colorama import Fore, Style, init

from .models import CampaignBrief, AspectRatio, GeneratedAsset
from .brief_parser import BriefParser
from .asset_manager import AssetManager
from .image_generator import ImageGenerator
from .image_processor import ImageProcessor
from .content_moderator import ContentModerator
from .localizer import Localizer
from .brand_compliance import BrandComplianceChecker

# Initialize colorama for colored output
init(autoreset=True)


class CreativePipeline:
    """Orchestrates the creative automation pipeline."""
    
    def __init__(
        self,
        campaign_path: Path
    ):
        """
        Initialize the pipeline.
        
        Args:
            campaign_path: Path to campaign directory
        """
        self.campaign_path = Path(campaign_path)
        self.config = self._load_config()
        
        # Initialize components
        self.brief_parser = BriefParser()
        self.asset_manager = AssetManager(self.campaign_path)
        self.image_generator = ImageGenerator()
        self.image_processor = ImageProcessor()
        
        # Phase 2 components
        self.content_moderator = ContentModerator()
        self.localizer = Localizer()
        
        # Track generated assets
        self.generated_assets: List[GeneratedAsset] = []
        self.compliance_results = []
    
    def _load_config(self) -> dict:
        """Load default configuration."""
        # Default configuration
        return {
            'aspect_ratios': [
                {'name': 'square', 'ratio': [1, 1], 'width': 1080, 'height': 1080},
                {'name': 'story', 'ratio': [9, 16], 'width': 1080, 'height': 1920},
                {'name': 'landscape', 'ratio': [16, 9], 'width': 1920, 'height': 1080}
            ],
            'text_overlay': {
                'font_size_base': 72,
                'padding': 60,
                'text_color': '#FFFFFF',
                'stroke_color': '#000000',
                'stroke_width': 3,
                'position': 'bottom'
            }
        }
    
    def run(self, brief_filename: str = "brief.yaml") -> dict:
        """
        Run the complete pipeline.
        
        Args:
            brief_filename: Name of the brief file
            
        Returns:
            Dictionary with pipeline results and statistics
        """
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}Creative Automation Pipeline")
        print(f"{Fore.CYAN}{'='*60}\n")
        
        # Step 1: Parse brief
        print(f"{Fore.YELLOW}[1/5] Parsing campaign brief...")
        brief_path = self.campaign_path / brief_filename
        brief = self.brief_parser.parse(brief_path)
        
        is_valid, warnings = self.brief_parser.validate_brief(brief)
        if not is_valid:
            raise ValueError(f"Invalid brief: {warnings}")
        
        if warnings:
            for warning in warnings:
                print(f"{Fore.YELLOW}  ⚠ {warning}")
        
        print(f"{Fore.GREEN}  ✓ Brief loaded: {brief.campaign_id}")
        print(f"  ✓ Products: {len(brief.products)}")
        
        # Step 1.5: Content Moderation (Phase 2)
        print(f"\n{Fore.YELLOW}[Phase 2] Content moderation...")
        if not self.content_moderator.moderate_campaign_message(brief.campaign_message):
            print(f"{Fore.RED}  ✗ Campaign message flagged by moderation")
        else:
            print(f"{Fore.GREEN}  ✓ Campaign message passed moderation")
        
        # Step 1.6: Localization (Phase 2)
        original_message = brief.campaign_message
        if brief.target_market.language != 'en-US' and brief.target_market.language != 'en':
            print(f"\n{Fore.YELLOW}[Phase 2] Localizing to {brief.target_market.language}...")
            target_lang = brief.target_market.language.split('-')[0]  # Get base language code
            brief.campaign_message = self.localizer.translate_text(
                brief.campaign_message,
                target_lang
            )
            print(f"{Fore.GREEN}  ✓ Message localized: '{brief.campaign_message}'")
            
            # Update font for language
            if brief.brand_elements:
                original_font = brief.brand_elements.font
                brief.brand_elements.font = self.localizer.get_font_for_language(target_lang)
                if brief.brand_elements.font != original_font:
                    print(f"{Fore.GREEN}  ✓ Font adjusted for language: {brief.brand_elements.font}")
        
        # Step 2: Process each product
        print(f"\n{Fore.YELLOW}[2/7] Processing products...")
        
        for product in brief.products:
            print(f"\n{Fore.CYAN}  Product: {product.name}")
            
            # Check for existing hero image
            hero_image_path = self.asset_manager.find_asset(product.hero_image)
            
            if hero_image_path:
                print(f"{Fore.GREEN}    ✓ Using existing image: {hero_image_path.name}")
                hero_image = self.asset_manager.load_image(hero_image_path)
                source = "existing"
                prompt_used = None
            else:
                print(f"{Fore.YELLOW}    ⚡ Generating new image with AI...")
                brand_color = brief.brand_elements.primary_color if brief.brand_elements else None
                hero_image, prompt_used = self.image_generator.generate_with_retry(
                    product.name,
                    product.description,
                    brief.target_audience,
                    brand_color
                )
                print(f"{Fore.GREEN}    ✓ Image generated")
                source = "generated"
            
            # Step 3: Generate variants for each aspect ratio
            print(f"\n{Fore.YELLOW}[3/7] Creating aspect ratio variants...")
            
            for ratio_config in self.config['aspect_ratios']:
                ratio = AspectRatio(**ratio_config)
                print(f"    → {ratio.name} ({ratio.width}x{ratio.height})")
                
                # Resize image
                resized = self.image_processor.resize_for_aspect_ratio(
                    hero_image,
                    ratio.width,
                    ratio.height
                )
                
                # Add text overlay
                text_config = self.config['text_overlay']
                with_text = self.image_processor.add_text_overlay(
                    resized,
                    brief.campaign_message,
                    position=text_config['position'],
                    font_size=text_config['font_size_base'],
                    text_color=text_config['text_color'],
                    stroke_color=text_config['stroke_color'],
                    stroke_width=text_config['stroke_width'],
                    padding=text_config['padding']
                )
                
                # Add logo if available
                if brief.brand_elements and brief.brand_elements.logo:
                    logo_path = self.asset_manager.find_asset(brief.brand_elements.logo)
                    if logo_path:
                        with_text = self.image_processor.add_logo(
                            with_text,
                            logo_path,
                            position="top-right"
                        )
                
                # Step 4: Brand Compliance Check (Phase 2)
                if ratio.name == 'square':  # Only check once per product
                    print(f"\n{Fore.YELLOW}[Phase 2] Running brand compliance checks...")
                    compliance_checker = BrandComplianceChecker(
                        brand_color=brief.brand_elements.primary_color if brief.brand_elements else None,
                        logo_path=logo_path if brief.brand_elements and brief.brand_elements.logo else None
                    )
                    compliance_result = compliance_checker.run_brand_checks(with_text)
                    self.compliance_results.append({
                        'product_id': product.id,
                        'product_name': product.name,
                        'compliance': compliance_result
                    })
                    
                    # Display compliance results
                    if compliance_result['overall_passed']:
                        print(f"{Fore.GREEN}    ✓ Compliance: PASSED (Score: {compliance_result['overall_score']}/100)")
                    else:
                        print(f"{Fore.YELLOW}    ⚠ Compliance: REVIEW NEEDED (Score: {compliance_result['overall_score']}/100)")
                
                # Save output
                output_path = self.asset_manager.save_output(
                    with_text,
                    product.id,
                    ratio.name
                )
                
                # Track generated asset
                self.generated_assets.append(GeneratedAsset(
                    product_id=product.id,
                    product_name=product.name,
                    aspect_ratio=ratio.name,
                    file_path=str(output_path),
                    source=source,
                    prompt_used=prompt_used
                ))
                
                print(f"{Fore.GREEN}      ✓ Saved: {output_path.relative_to(self.campaign_path)}")
        
        # Step 5: Generate report
        print(f"\n{Fore.YELLOW}[5/7] Generating report...")
        report = self._generate_report(brief, original_message)
        report_path = self.campaign_path / "output" / "generation_report.yaml"
        with open(report_path, 'w') as f:
            yaml.dump(report, f, default_flow_style=False, sort_keys=False)
        print(f"{Fore.GREEN}  ✓ Report saved: {report_path.relative_to(self.campaign_path)}")
        
        # Step 6: Summary
        print(f"\n{Fore.YELLOW}[6/7] Pipeline complete!")
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.GREEN}Summary:")
        print(f"  • Campaign: {brief.campaign_id}")
        print(f"  • Products processed: {len(brief.products)}")
        print(f"  • Total assets generated: {len(self.generated_assets)}")
        
        # Phase 2 summary
        if brief.target_market.language not in ['en', 'en-US']:
            print(f"  • Localized to: {brief.target_market.language}")
        compliance_passed = sum(1 for r in self.compliance_results if r['compliance']['overall_passed'])
        print(f"  • Compliance checks: {compliance_passed}/{len(self.compliance_results)} passed")
        
        print(f"  • Output directory: {self.campaign_path / 'output'}")
        print(f"{Fore.CYAN}{'='*60}\n")
        
        return report
    
    def _generate_report(self, brief: CampaignBrief, original_message: str) -> dict:
        """Generate a detailed report of the pipeline execution."""
        report = {
            'campaign_id': brief.campaign_id,
            'timestamp': str(Path.cwd()),  # Placeholder
            'phase_2_features': {
                'content_moderation': 'enabled',
                'localization': {
                    'enabled': brief.target_market.language not in ['en', 'en-US'],
                    'target_language': brief.target_market.language,
                    'original_message': original_message,
                    'localized_message': brief.campaign_message if brief.target_market.language not in ['en', 'en-US'] else None
                },
                'brand_compliance': 'enabled'
            },
            'products': [],
            'statistics': {
                'total_products': len(brief.products),
                'total_assets': len(self.generated_assets),
                'assets_generated': len([a for a in self.generated_assets if a.source == 'generated']),
                'assets_reused': len([a for a in self.generated_assets if a.source == 'existing']),
                'compliance_passed': sum(1 for r in self.compliance_results if r['compliance']['overall_passed']),
                'compliance_total': len(self.compliance_results)
            }
        }
        
        # Group assets by product
        for product in brief.products:
            product_assets = [a for a in self.generated_assets if a.product_id == product.id]
            
            # Find compliance result for this product
            compliance_data = next(
                (r['compliance'] for r in self.compliance_results if r['product_id'] == product.id),
                None
            )
            
            product_report = {
                'product_id': product.id,
                'product_name': product.name,
                'source': product_assets[0].source if product_assets else 'unknown',
                'prompt_used': product_assets[0].prompt_used if product_assets else None,
                'compliance': compliance_data,
                'variants': [
                    {
                        'aspect_ratio': asset.aspect_ratio,
                        'file_path': asset.file_path
                    }
                    for asset in product_assets
                ]
            }
            report['products'].append(product_report)
        
        return report
