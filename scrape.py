#!/usr/bin/env python3
"""
Main script to scrape YouTube channel data.
Supports incremental scraping - only processes new videos.
"""
import argparse
import sys
from pathlib import Path
from dotenv import load_dotenv
import os

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.database.models import Database
from src.scraper.youtube_scraper import YouTubeScraper
from src.utils.logger import setup_logger


def main():
    """Main entry point for the scraper."""
    parser = argparse.ArgumentParser(
        description='Scrape YouTube channel videos (incremental)'
    )
    parser.add_argument(
        '--channel-url',
        type=str,
        help='YouTube channel URL (overrides .env)'
    )
    parser.add_argument(
        '--db-path',
        type=str,
        default='data/youtube_data.db',
        help='Path to SQLite database (default: data/youtube_data.db)'
    )
    parser.add_argument(
        '--log-level',
        type=str,
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Logging level (default: INFO)'
    )
    parser.add_argument(
        '--log-file',
        type=str,
        help='Path to log file (optional)'
    )

    args = parser.parse_args()

    # Load environment variables
    load_dotenv()

    # Get channel URL
    channel_url = args.channel_url or os.getenv('CHANNEL_URL')
    if not channel_url:
        print("Error: Channel URL must be provided via --channel-url or CHANNEL_URL in .env")
        sys.exit(1)

    # Setup logging
    logger = setup_logger(
        name='youtube_scraper',
        log_file=args.log_file,
        level=args.log_level
    )

    logger.info("=" * 60)
    logger.info("YouTube Channel Scraper - Incremental Mode")
    logger.info("=" * 60)
    logger.info(f"Channel URL: {channel_url}")
    logger.info(f"Database: {args.db_path}")
    logger.info("-" * 60)

    try:
        # Initialize database
        logger.info("Initializing database...")
        db = Database(args.db_path)
        db.create_tables()
        logger.info("Database initialized successfully")

        # Initialize scraper
        logger.info("Initializing scraper...")
        scraper = YouTubeScraper(db)

        # Run incremental scrape
        logger.info("Starting incremental scrape...")
        stats = scraper.scrape_channel_incremental(channel_url)

        # Print summary
        logger.info("=" * 60)
        logger.info("Scraping Summary")
        logger.info("=" * 60)
        logger.info(f"Total videos in channel: {stats['total']}")
        logger.info(f"Already processed: {stats['skipped']}")
        logger.info(f"New videos found: {stats['new']}")
        logger.info(f"Successfully scraped: {stats['succeeded']}")
        logger.info(f"Failed: {stats['failed']}")
        logger.info("=" * 60)

        if stats['failed'] > 0:
            logger.warning(f"{stats['failed']} videos failed to process. Check logs for details.")

        logger.info("Scraping completed successfully!")

    except KeyboardInterrupt:
        logger.warning("\nScraping interrupted by user. Progress has been saved.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
