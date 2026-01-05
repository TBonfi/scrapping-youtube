"""
YouTube scraper using yt-dlp and youtube-transcript-api.
Implements incremental scraping to avoid re-processing existing videos.
"""
import logging
from datetime import datetime
from typing import List, Dict, Optional
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
from tqdm import tqdm

from src.database.models import Database, Video

logger = logging.getLogger(__name__)


class YouTubeScraper:
    """Scraper for YouTube channel data with incremental processing."""

    def __init__(self, db: Database):
        self.db = db
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'ignoreerrors': True,
        }

    def get_channel_videos(self, channel_url: str) -> List[Dict]:
        """
        Get all video URLs from a YouTube channel.

        Args:
            channel_url: URL of the YouTube channel

        Returns:
            List of dictionaries with video information
        """
        logger.info(f"Fetching videos from channel: {channel_url}")

        # Configure yt-dlp to get all videos from the channel
        ydl_opts = {
            **self.ydl_opts,
            'extract_flat': 'in_playlist',  # Don't download, just get metadata
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                # Extract channel info
                channel_info = ydl.extract_info(channel_url, download=False)

                if 'entries' not in channel_info:
                    logger.error("No videos found in channel")
                    return []

                videos = []
                for entry in channel_info['entries']:
                    if entry:  # Sometimes entries can be None
                        videos.append({
                            'video_id': entry.get('id'),
                            'title': entry.get('title'),
                            'url': entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id')}"
                        })

                logger.info(f"Found {len(videos)} videos in channel")
                return videos

            except Exception as e:
                logger.error(f"Error fetching channel videos: {e}")
                return []

    def get_video_metadata(self, video_id: str) -> Optional[Dict]:
        """
        Get detailed metadata for a single video.

        Args:
            video_id: YouTube video ID

        Returns:
            Dictionary with video metadata or None if error
        """
        url = f"https://www.youtube.com/watch?v={video_id}"

        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)

                # Parse upload date
                upload_date = None
                if info.get('upload_date'):
                    try:
                        upload_date = datetime.strptime(info['upload_date'], '%Y%m%d')
                    except ValueError:
                        logger.warning(f"Could not parse upload date: {info.get('upload_date')}")

                metadata = {
                    'video_id': video_id,
                    'title': info.get('title'),
                    'description': info.get('description'),
                    'upload_date': upload_date,
                    'duration_seconds': info.get('duration'),
                    'view_count': info.get('view_count'),
                    'like_count': info.get('like_count'),
                    'comment_count': info.get('comment_count'),
                    'url': url,
                    'thumbnail_url': info.get('thumbnail'),
                }

                return metadata

            except Exception as e:
                logger.error(f"Error getting metadata for {video_id}: {e}")
                return None

    def get_transcript(self, video_id: str, languages: List[str] = ['es', 'en']) -> Optional[Dict]:
        """
        Get transcript for a video.

        Args:
            video_id: YouTube video ID
            languages: List of language codes to try (in order of preference)

        Returns:
            Dictionary with transcript text and language, or None if not available
        """
        try:
            # Try to get transcript in preferred languages
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

            # Try manual transcripts first (more accurate)
            for lang in languages:
                try:
                    transcript = transcript_list.find_manually_created_transcript([lang])
                    transcript_data = transcript.fetch()
                    text = ' '.join([entry['text'] for entry in transcript_data])
                    logger.info(f"Found manual transcript for {video_id} in {lang}")
                    return {
                        'text': text,
                        'language': lang,
                        'type': 'manual'
                    }
                except:
                    continue

            # Try auto-generated transcripts
            for lang in languages:
                try:
                    transcript = transcript_list.find_generated_transcript([lang])
                    transcript_data = transcript.fetch()
                    text = ' '.join([entry['text'] for entry in transcript_data])
                    logger.info(f"Found auto-generated transcript for {video_id} in {lang}")
                    return {
                        'text': text,
                        'language': lang,
                        'type': 'auto'
                    }
                except:
                    continue

            logger.warning(f"No transcript found for {video_id} in languages: {languages}")
            return None

        except TranscriptsDisabled:
            logger.warning(f"Transcripts disabled for video {video_id}")
            return None
        except NoTranscriptFound:
            logger.warning(f"No transcript found for video {video_id}")
            return None
        except Exception as e:
            logger.error(f"Error getting transcript for {video_id}: {e}")
            return None

    def process_video(self, video_id: str) -> bool:
        """
        Process a single video: get metadata and transcript, save to database.

        Args:
            video_id: YouTube video ID

        Returns:
            True if successful, False otherwise
        """
        session = self.db.get_session()

        try:
            # Get metadata
            logger.info(f"Processing video: {video_id}")
            metadata = self.get_video_metadata(video_id)

            if not metadata:
                # Save failed status
                video = Video(
                    video_id=video_id,
                    title="Unknown",
                    url=f"https://www.youtube.com/watch?v={video_id}",
                    processing_status='failed',
                    error_message='Failed to fetch metadata'
                )
                session.add(video)
                session.commit()
                return False

            # Get transcript
            transcript_data = self.get_transcript(video_id)

            # Create video object
            video = Video(
                **metadata,
                transcript=transcript_data['text'] if transcript_data else None,
                transcript_language=transcript_data['language'] if transcript_data else None,
                has_transcript=transcript_data is not None,
                processing_status='completed',
                scraped_at=datetime.utcnow(),
                last_updated=datetime.utcnow()
            )

            session.add(video)
            session.commit()

            logger.info(f"Successfully processed video: {video_id} - {metadata['title']}")
            return True

        except Exception as e:
            logger.error(f"Error processing video {video_id}: {e}")
            session.rollback()

            # Try to save error status
            try:
                video = Video(
                    video_id=video_id,
                    title="Unknown",
                    url=f"https://www.youtube.com/watch?v={video_id}",
                    processing_status='failed',
                    error_message=str(e)
                )
                session.add(video)
                session.commit()
            except:
                pass

            return False

        finally:
            session.close()

    def scrape_channel_incremental(self, channel_url: str) -> Dict[str, int]:
        """
        Scrape a YouTube channel incrementally (only new videos).

        Args:
            channel_url: URL of the YouTube channel

        Returns:
            Dictionary with statistics (total, new, failed)
        """
        # Get all videos from channel
        all_videos = self.get_channel_videos(channel_url)

        if not all_videos:
            logger.warning("No videos found to process")
            return {'total': 0, 'new': 0, 'skipped': 0, 'failed': 0}

        # Get already processed video IDs
        processed_ids = self.db.get_processed_video_ids()
        logger.info(f"Found {len(processed_ids)} already processed videos")

        # Filter to only new videos
        new_videos = [v for v in all_videos if v['video_id'] not in processed_ids]

        stats = {
            'total': len(all_videos),
            'new': len(new_videos),
            'skipped': len(processed_ids),
            'failed': 0,
            'succeeded': 0
        }

        if not new_videos:
            logger.info("No new videos to process")
            return stats

        logger.info(f"Processing {len(new_videos)} new videos...")

        # Process each new video
        for video in tqdm(new_videos, desc="Scraping videos"):
            success = self.process_video(video['video_id'])
            if success:
                stats['succeeded'] += 1
            else:
                stats['failed'] += 1

        logger.info(f"Scraping completed: {stats['succeeded']} succeeded, {stats['failed']} failed")
        return stats
