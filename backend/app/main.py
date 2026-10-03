from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import engine, Base, SessionLocal
from .models import User, DatingProfile
from .routers import auth, connections, dating

# Create database tables automatically
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Privacy-First Authentication, Safe Connections, and Consent-Based LGBTQ+ Platform Backend",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router)
app.include_router(connections.router)
app.include_router(dating.router)

@app.get("/")
def root():
    return {
        "status": "online",
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "principle": "Zero forced identity exposure, 100% consent-driven"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Auto-seed sample members if database is empty for immediate demonstration
@app.on_event("startup")
def seed_sample_members():
    db = SessionLocal()
    try:
        user_count = db.query(User).count()
        if user_count == 0:
            sample_users = [
                {
                    "alias": "VelvetFalcon",
                    "pronouns": "she/they",
                    "city": "Pune",
                    "headline": "Queer literature enthusiast & indie game dev",
                    "bio": "Always up for hot coffee, discussing graphic novels, and sharing safe indie art spaces in Pune.",
                    "interests": "Queer Lit, Video Games, Coffee, Poetry",
                    "intent": "Friendship & Dating"
                },
                {
                    "alias": "Solaris_TG",
                    "pronouns": "she/her",
                    "city": "Delhi NCR",
                    "headline": "Trans advocate, tech researcher, weekend painter",
                    "bio": "Navigating medical transition and corporate DEI. Looking for genuine friends to explore Delhi cafes.",
                    "interests": "Trans Advocacy, Painting, Tech, Nature Walks",
                    "intent": "Friendship & Mentorship"
                },
                {
                    "alias": "CosmicVoyager",
                    "pronouns": "he/him",
                    "city": "Bengaluru",
                    "headline": "Backend engineer, vinyl collector, amateur baker",
                    "bio": "Introverted gay guy living in Koramangala. Let's trade sourdough recipes or vinyl recommendations.",
                    "interests": "Baking, Vinyl Records, Coding, Sci-Fi",
                    "intent": "Dating & Long-term"
                }
            ]
            for s in sample_users:
                u = User(
                    alias=s["alias"],
                    is_anonymous=True,
                    pronouns=s["pronouns"],
                    city=s["city"],
                    identity_tags="Queer, Safe Verified"
                )
                db.add(u)
                db.commit()
                db.refresh(u)

                dp = DatingProfile(
                    user_id=u.id,
                    opt_in_dating=True,
                    headline=s["headline"],
                    bio=s["bio"],
                    interests=s["interests"],
                    intent=s["intent"],
                    approx_city=s["city"]
                )
                db.add(dp)
            db.commit()
    finally:
        db.close()
