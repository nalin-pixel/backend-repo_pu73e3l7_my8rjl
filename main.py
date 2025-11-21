import os
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import db, create_document, get_documents

app = FastAPI(title="Esports Committee API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Pydantic response models ----------
class EventOut(BaseModel):
    id: Optional[str] = None
    title: str
    description: str
    date: datetime
    game: str
    location: str
    cover_image: Optional[str] = None
    gallery_urls: List[str] = []
    status: str


class GalleryItemOut(BaseModel):
    id: Optional[str] = None
    url: str
    caption: Optional[str] = None
    event_id: Optional[str] = None


class TeamMemberOut(BaseModel):
    id: Optional[str] = None
    name: str
    role: str
    avatar_url: Optional[str] = None
    twitter: Optional[str] = None
    instagram: Optional[str] = None
    discord: Optional[str] = None
    bio: Optional[str] = None


# ---------- Seed helper ----------
async def seed_if_empty():
    if db is None:
        return

    # Seed events
    if db["event"].count_documents({}) == 0:
        sample_events = [
            {
                "title": "Valorant Showdown 2024",
                "description": "Inter-college 5v5 tournament with live shoutcasting.",
                "date": datetime(2024, 10, 12, 14, 0, tzinfo=timezone.utc),
                "game": "Valorant",
                "location": "Main Auditorium + Twitch",
                "cover_image": "https://images.unsplash.com/photo-1605647512339-1644ff3d63a8?q=80&w=1600&auto=format&fit=crop",
                "gallery_urls": [],
                "status": "past",
            },
            {
                "title": "Rocket League Freshers Cup",
                "description": "2v2 rocket-powered soccer spectacular.",
                "date": datetime(2025, 1, 20, 16, 0, tzinfo=timezone.utc),
                "game": "Rocket League",
                "location": "Esports Lab",
                "cover_image": "https://images.unsplash.com/photo-1511735111819-9a3f7709049c?q=80&w=1600&auto=format&fit=crop",
                "gallery_urls": [],
                "status": "upcoming",
            },
            {
                "title": "CS2 LAN Night",
                "description": "Casual brackets, pro vibes. BYO peripherals.",
                "date": datetime(2024, 11, 5, 18, 30, tzinfo=timezone.utc),
                "game": "Counter-Strike 2",
                "location": "Innovation Hub",
                "cover_image": "https://images.unsplash.com/photo-1542751371-adc38448a05e?q=80&w=1600&auto=format&fit=crop",
                "gallery_urls": [],
                "status": "past",
            },
        ]
        for e in sample_events:
            create_document("event", e)

    # Seed team
    if db["teammember"].count_documents({}) == 0:
        members = [
            {
                "name": "Aarav Kapoor",
                "role": "President",
                "avatar_url": "https://images.unsplash.com/photo-1547425260-76bcadfb4f2c?q=80&w=800&auto=format&fit=crop",
                "twitter": "",
                "instagram": "@aarav.gg",
                "discord": "aarav#1024",
                "bio": "Leading the charge to make campus esports legendary.",
            },
            {
                "name": "Meera Shah",
                "role": "Events Lead",
                "avatar_url": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?q=80&w=800&auto=format&fit=crop",
                "instagram": "@meeracalls",
                "discord": "meerashah#2255",
                "bio": "Crafting unforgettable brackets and hype moments.",
            },
            {
                "name": "Rohan Das",
                "role": "Broadcast & Production",
                "avatar_url": "https://images.unsplash.com/photo-1527980965255-d3b416303d12?q=80&w=800&auto=format&fit=crop",
                "instagram": "@rohancuts",
                "discord": "rohandas#7744",
                "bio": "Cameras, overlays, replays – all the magic behind the stream.",
            },
        ]
        for m in members:
            create_document("teammember", m)

    # Seed gallery
    if db["galleryimage"].count_documents({}) == 0:
        gallery = [
            {
                "url": "https://images.unsplash.com/photo-1542751110-97427bbecf20?q=80&w=1600&auto=format&fit=crop",
                "caption": "LAN vibes",
            },
            {
                "url": "https://images.unsplash.com/photo-1511512578047-dfb367046420?q=80&w=1600&auto=format&fit=crop",
                "caption": "Clutch moment",
            },
            {
                "url": "https://images.unsplash.com/photo-1511379938547-c1f69419868d?q=80&w=1600&auto=format&fit=crop",
                "caption": "Caster desk",
            },
            {
                "url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?q=80&w=1600&auto=format&fit=crop",
                "caption": "Headset check",
            },
        ]
        for g in gallery:
            create_document("galleryimage", g)


@app.on_event("startup")
async def on_startup():
    try:
        await seed_if_empty()
    except Exception:
        # seeding best-effort only
        pass


@app.get("/")
def root():
    return {"message": "Esports Committee Backend running"}


@app.get("/api/events", response_model=List[EventOut])
def list_events(status: Optional[str] = Query(default=None, regex="^(past|upcoming)$")):
    filt = {}
    if status:
        filt["status"] = status
    docs = get_documents("event", filt)
    out = []
    for d in docs:
        d["id"] = str(d.get("_id"))
        d.pop("_id", None)
        out.append(d)
    # Sort by date descending for past, ascending for upcoming
    if status == "past":
        out.sort(key=lambda x: x["date"], reverse=True)
    elif status == "upcoming":
        out.sort(key=lambda x: x["date"]) 
    return out


@app.get("/api/gallery", response_model=List[GalleryItemOut])
def list_gallery(limit: int = 24):
    docs = get_documents("galleryimage", {}, limit=limit)
    out = []
    for d in docs:
        d["id"] = str(d.get("_id"))
        d.pop("_id", None)
        out.append(d)
    return out


@app.get("/api/team", response_model=List[TeamMemberOut])
def list_team():
    docs = get_documents("teammember")
    out = []
    for d in docs:
        d["id"] = str(d.get("_id"))
        d.pop("_id", None)
        out.append(d)
    return out


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": [],
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
