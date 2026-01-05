#!/usr/bin/env python3
"""Script to check what's in the database."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.database.models import Database, Video

db = Database('data/youtube_data.db')
session = db.get_session()

print("=" * 80)
print("DATABASE CONTENTS")
print("=" * 80)

videos = session.query(Video).all()

print(f"\nTotal videos in database: {len(videos)}\n")

for video in videos:
    print("-" * 80)
    print(f"Video ID: {video.video_id}")
    print(f"Title: {video.title}")
    print(f"URL: {video.url}")
    print(f"Upload date: {video.upload_date}")
    print(f"Duration: {video.duration_seconds} seconds")
    print(f"Views: {video.view_count}")
    print(f"Likes: {video.like_count}")
    print(f"Has transcript: {video.has_transcript}")
    print(f"Transcript language: {video.transcript_language}")
    if video.transcript:
        print(f"Transcript length: {len(video.transcript)} characters")
        print(f"Transcript preview: {video.transcript[:200]}...")
    print(f"Status: {video.processing_status}")
    if video.error_message:
        print(f"Error: {video.error_message}")
    print(f"Scraped at: {video.scraped_at}")

print("\n" + "=" * 80)

# Summary by status
from sqlalchemy import func
status_counts = session.query(Video.processing_status, func.count(Video.video_id)).group_by(Video.processing_status).all()

print("\nSUMMARY BY STATUS:")
for status, count in status_counts:
    print(f"  {status}: {count}")

# Transcript availability
transcript_counts = session.query(Video.has_transcript, func.count(Video.video_id)).group_by(Video.has_transcript).all()

print("\nTRANSCRIPT AVAILABILITY:")
for has_transcript, count in transcript_counts:
    print(f"  {'Has transcript' if has_transcript else 'No transcript'}: {count}")

session.close()
