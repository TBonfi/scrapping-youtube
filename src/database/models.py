"""
Database models for YouTube video data.
"""
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Video(Base):
    """Model for storing YouTube video data."""

    __tablename__ = 'videos'

    # Primary key
    video_id = Column(String(20), primary_key=True)

    # Metadata
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    upload_date = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)

    # Engagement metrics
    view_count = Column(Integer, nullable=True)
    like_count = Column(Integer, nullable=True)
    comment_count = Column(Integer, nullable=True)

    # URLs and thumbnails
    url = Column(String(200), nullable=False)
    thumbnail_url = Column(String(500), nullable=True)

    # Transcript
    transcript = Column(Text, nullable=True)
    transcript_language = Column(String(10), nullable=True)
    has_transcript = Column(Boolean, default=False)

    # Processing status
    scraped_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    processing_status = Column(String(20), default='pending')  # pending, completed, failed
    error_message = Column(Text, nullable=True)

    def __repr__(self):
        return f"<Video(video_id='{self.video_id}', title='{self.title[:50]}...')>"


class Database:
    """Database manager class."""

    def __init__(self, db_path: str):
        self.engine = create_engine(f'sqlite:///{db_path}')
        self.Session = sessionmaker(bind=self.engine)

    def create_tables(self):
        """Create all tables if they don't exist."""
        Base.metadata.create_all(self.engine)

    def get_session(self):
        """Get a new database session."""
        return self.Session()

    def get_processed_video_ids(self):
        """Get set of all video IDs that have been processed."""
        session = self.get_session()
        try:
            video_ids = session.query(Video.video_id).all()
            return {vid[0] for vid in video_ids}
        finally:
            session.close()
