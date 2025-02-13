import httpx
from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List, Optional
import uuid

app = FastAPI()

# Simulación de base de datos en memoria
jobs = []

# URL del servicio externo
EXTERNAL_JOBS_URL = "http://localhost:8081/jobs"  


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


# Nuevo endpoint para buscar en ambas fuentes
@app.get("/jobs/search/", response_model=List[Job])
def search_jobs(
    title: Optional[str] = Query(None, min_length=2),
    company: Optional[str] = Query(None, min_length=2),
    location: Optional[str] = Query(None, min_length=2)
):
    results = jobs.copy()  # Copia trabajos internos
    
    # Obtener datos de jobberwocky-extra-source
    try:
        response = httpx.get(EXTERNAL_JOBS_URL, timeout=5)
        if response.status_code == 200:
            external_jobs = response.json()
            for ext_job in external_jobs:
                # Limpiar y estandarizar el formato
                job = Job(
                    id=str(uuid.uuid4()),
                    title=ext_job.get("jobTitle", "Unknown Title"),
                    company=ext_job.get("companyName", "Unknown Company"),
                    location=ext_job.get("jobLocation", "Unknown Location"),
                    description=ext_job.get("jobDescription", "No description available")
                )
                results.append(job)
    except Exception as e:
        print(f"Error fetching external jobs: {e}")

    # Filtrar resultados según la búsqueda
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
