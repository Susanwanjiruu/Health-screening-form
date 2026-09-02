from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from core.config import settings
from core.security import limiter
from database import Base, engine


import screening.models  

from screening.routers import (
    auth_router, user_router, facility_router, center_router,
    beneficiary_router, screening_router, referral_router, report_router,
    audit_router,
)

app = FastAPI(title=settings.PROJECT_NAME, version="2.0")


app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router, prefix=settings.API_V1_STR)
app.include_router(user_router.router, prefix=settings.API_V1_STR)
app.include_router(facility_router.router, prefix=settings.API_V1_STR)
app.include_router(center_router.router, prefix=settings.API_V1_STR)
app.include_router(beneficiary_router.router, prefix=settings.API_V1_STR)
app.include_router(screening_router.router, prefix=settings.API_V1_STR)
app.include_router(referral_router.router, prefix=settings.API_V1_STR)
app.include_router(report_router.router, prefix=settings.API_V1_STR)
app.include_router(audit_router.router, prefix=settings.API_V1_STR)


@app.on_event("startup")
def create_tables():
    
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": settings.PROJECT_NAME, "status": "running"}
