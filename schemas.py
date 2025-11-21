"""
Database Schemas for the E-sports Committee site

Each Pydantic model represents a MongoDB collection. The collection name is the
lowercase class name (e.g., Event -> "event").
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional
from datetime import datetime


class Event(BaseModel):
    """
    Esports events (past and upcoming)
    Collection: "event"
    """
    title: str = Field(..., description="Event title")
    description: str = Field(..., description="Short description of the event")
    date: datetime = Field(..., description="Event date and time (UTC)")
    game: str = Field(..., description="Primary game or category")
    location: str = Field(..., description="Venue or online platform")
    cover_image: Optional[HttpUrl] = Field(None, description="Hero/cover image URL")
    gallery_urls: List[HttpUrl] = Field(default_factory=list, description="Related images")
    status: str = Field(..., pattern="^(past|upcoming)$", description="past | upcoming")


class Galleryimage(BaseModel):
    """
    Photo gallery items
    Collection: "galleryimage"
    """
    url: HttpUrl
    caption: Optional[str] = None
    event_id: Optional[str] = Field(None, description="Related event id as string")


class Teammember(BaseModel):
    """
    Committee team members
    Collection: "teammember"
    """
    name: str
    role: str
    avatar_url: Optional[HttpUrl] = None
    twitter: Optional[str] = None
    instagram: Optional[str] = None
    discord: Optional[str] = None
    bio: Optional[str] = None
