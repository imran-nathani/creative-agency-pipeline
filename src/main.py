"""Command-line interface for the creative automation pipeline."""
import click
from pathlib import Path
import sys
import os
from dotenv import load_dotenv

from .pipeline import CreativePipeline

# Load environment variables from .env file
load_dotenv()


@click.command()
@click.argument('campaign_path', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option(
    '--brief',
    default='brief.yaml',
    help='Name of the brief file (default: brief.yaml)'
)

def main(campaign_path: str, brief: str):
    """
    Creative Automation Pipeline
    
    Generate social media campaign assets from a campaign brief.
    
    CAMPAIGN_PATH: Path to the campaign directory containing brief.yaml and assets/
    
    Example:
        python -m src.main campaign/AcmeShampoo
    """
    try:
        # Initialize and run pipeline
        pipeline = CreativePipeline(
            campaign_path=Path(campaign_path)
        )
        
        report = pipeline.run(brief_filename=brief)
        
        click.echo(click.style("\n✓ Pipeline completed successfully!", fg='green', bold=True))
        
    except FileNotFoundError as e:
        click.echo(click.style(f"Error: {e}", fg='red'))
        sys.exit(1)
    except ValueError as e:
        click.echo(click.style(f"Validation Error: {e}", fg='red'))
        sys.exit(1)
    except Exception as e:
        click.echo(click.style(f"Pipeline Error: {e}", fg='red'))
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
