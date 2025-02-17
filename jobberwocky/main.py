import httpx
from fastapi import FastAPI, Query
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import uuid
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logging.basicConfig(level=logging.INFO)

app = FastAPI()

# Simulación de base de datos en memoria
jobs = []
subscribers = []

# URL del servicio externo
EXTERNAL_JOBS_URL = "http://localhost:8081/jobs"


class Job(BaseModel):
    id: str = str(uuid.uuid4())
    title: str
    company: str
    location: str
    description: str


class Subscription(BaseModel):
    email: EmailStr
    keyword: Optional[str] = None  # Patrón de búsqueda


@app.post("/jobs/")
def create_job(job: Job):
    jobs.append(job)
    notify_subscribers(job)
    return {"message": "Job created", "job": job}


@app.get("/jobs/", response_model=List[Job])
def get_jobs():
    return jobs

#  Endpoint /subscribe/ para que los candidatos se registren con su correo y un filtro de búsqueda opcional.
@app.post("/subscribe/")
def subscribe(subscription: Subscription):
    subscribers.append(subscription)
    return {"message": "Subscription successful", "subscription": subscription}


def notify_subscribers(job: Job):
    """Envía correos electrónicos a los suscriptores que coincidan con el patrón de búsqueda."""
    for subscriber in subscribers:
        if not subscriber.keyword or subscriber.keyword.lower() in job.title.lower():
            send_email(subscriber.email, job)


def send_email(to_email: str, job: Job):
    """Envía un email de notificación con los detalles de la oferta de trabajo."""
    sender_email = "facundomedero26@gmail.com"
    sender_password = "your-password"  # Usa variables de entorno en producción

    subject = f"New Job Alert: {job.title}"
    body = f"""
    A new job matching your interest has been posted!

    **Title:** {job.title}
    **Company:** {job.company}
    **Location:** {job.location}
    **Description:** {job.description}

    Visit our site for more details!
    """

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, msg.as_string())
        logging.info(f"Email sent to {to_email}")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
