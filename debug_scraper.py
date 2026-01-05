#!/usr/bin/env python3
"""Debug script to test scraping functionality."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import yt_dlp
from src.utils.logger import setup_logger

logger = setup_logger(level='DEBUG')

# Test channel URL
channel_url = "https://www.youtube.com/@Historias.Innecesarias"

logger.info(f"Testing channel: {channel_url}")

# Test 1: Get channel videos
logger.info("=" * 60)
logger.info("TEST 1: Fetching channel videos")
logger.info("=" * 60)

ydl_opts = {
    'quiet': False,
    'no_warnings': False,
    'extract_flat': 'in_playlist',
    'ignoreerrors': True,
}

try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        logger.info("Extracting channel info...")
        channel_info = ydl.extract_info(channel_url, download=False)

        logger.info(f"Channel title: {channel_info.get('title', 'N/A')}")
        logger.info(f"Channel ID: {channel_info.get('id', 'N/A')}")
        logger.info(f"Has entries: {'entries' in channel_info}")

        if 'entries' in channel_info:
            entries = [e for e in channel_info['entries'] if e]
            logger.info(f"Total videos found: {len(entries)}")

            # Show first 3 videos
            for i, entry in enumerate(entries[:3]):
                logger.info(f"\nVideo {i+1}:")
                logger.info(f"  ID: {entry.get('id')}")
                logger.info(f"  Title: {entry.get('title')}")
                logger.info(f"  URL: {entry.get('url')}")

            # Test detailed extraction for first video
            if entries:
                logger.info("\n" + "=" * 60)
                logger.info("TEST 2: Fetching detailed metadata for first video")
                logger.info("=" * 60)

                first_video_id = entries[0].get('id')
                video_url = f"https://www.youtube.com/watch?v={first_video_id}"

                ydl_opts_detail = {
                    'quiet': False,
                    'no_warnings': False,
                    'extract_flat': False,
                }

                with yt_dlp.YoutubeDL(ydl_opts_detail) as ydl2:
                    logger.info(f"Extracting info for: {video_url}")
                    video_info = ydl2.extract_info(video_url, download=False)

                    logger.info(f"\nVideo ID: {video_info.get('id')}")
                    logger.info(f"Title: {video_info.get('title')}")
                    logger.info(f"Upload date: {video_info.get('upload_date')}")
                    logger.info(f"Duration: {video_info.get('duration')} seconds")
                    logger.info(f"Views: {video_info.get('view_count')}")
                    logger.info(f"Likes: {video_info.get('like_count')}")
                    logger.info(f"Description length: {len(video_info.get('description', ''))}")

                # Test transcript
                logger.info("\n" + "=" * 60)
                logger.info("TEST 3: Fetching transcript")
                logger.info("=" * 60)

                from youtube_transcript_api import YouTubeTranscriptApi

                try:
                    transcript_list = YouTubeTranscriptApi.list_transcripts(first_video_id)
                    logger.info(f"Available transcripts for {first_video_id}:")

                    for transcript in transcript_list:
                        logger.info(f"  - {transcript.language} ({transcript.language_code}) - Generated: {transcript.is_generated}")

                    # Try to get Spanish transcript
                    try:
                        transcript = transcript_list.find_transcript(['es'])
                        transcript_data = transcript.fetch()
                        logger.info(f"\nSpanish transcript found!")
                        logger.info(f"Number of segments: {len(transcript_data)}")
                        logger.info(f"First segment: {transcript_data[0] if transcript_data else 'N/A'}")
                    except Exception as e:
                        logger.warning(f"Could not get Spanish transcript: {e}")

                except Exception as e:
                    logger.error(f"Error getting transcript: {e}")
        else:
            logger.error("No entries found in channel info")
            logger.info(f"Channel info keys: {list(channel_info.keys())}")

except Exception as e:
    logger.error(f"Error: {e}", exc_info=True)
