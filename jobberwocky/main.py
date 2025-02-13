from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List, Optional
import uuid

app = FastAPI()

# Simulación de base de datos en memoria
jobs = []

class Job(BaseModel):
    id: str = str(uuid.uuid4())
    title: str
    company: str
    location: str
    description: str

@app.post("/jobs/")
def create_job(job: Job):
    jobs.append(job)
    return {"message": "Job created", "job": job}

@app.get("/jobs/", response_model=List[Job])
def get_jobs():
    return jobs

# ✅ Nuevo endpoint de búsqueda
@app.get("/jobs/search/", response_model=List[Job])
def search_jobs(
    title: Optional[str] = Query(None, min_length=2, description="Filter by job title"),
    company: Optional[str] = Query(None, min_length=2, description="Filter by company name"),
    location: Optional[str] = Query(None, min_length=2, description="Filter by location")
):
    results = jobs
    if title:
        results = [job for job in results if title.lower() in job.title.lower()]
    if company:
        results = [job for job in results if company.lower() in job.company.lower()]
    if location:
        results = [job for job in results if location.lower() in job.location.lower()]
    
    return results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
