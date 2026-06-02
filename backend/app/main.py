from app.db.session import get_db
from app.routes.resumes import router as resume_router
from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

app = FastAPI()

@app.get("/")
async def root():
    return { "message": "Hello Ankush" }

@app.get("/db-health")
def healthcheck(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT current_database();"))
    database_name = result.scalar()

    return {
        "status": "connected",
        "database": database_name
    }

app.include_router(resume_router)