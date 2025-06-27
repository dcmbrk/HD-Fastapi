from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user_model import Base as UserBase 
from app.models.explanation_model import Base as ExplanationBase 
from app.routers import user_router
from app.config import settings

SQLALCHEMY_DATABASE_URL = settings.database_url
engine = create_engine(SQLALCHEMY_DATABASE_URL)


UserBase.metadata.create_all(bind=engine)
ExplanationBase.metadata.create_all(bind=engine)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI(
    title="Phenikaa Help Desk API",
    description="API for managing help desk requests and user roles.",
    version="1.0.0",
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app.include_router(user_router.router)

@app.get("/")
async def read_root():
    return {"message": "Welcome to Phenikaa Help Desk FastAPI!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

