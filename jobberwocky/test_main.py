
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from jobberwocky.main import app

client = TestClient(app)

# Test 1: Crear un trabajo correctamente
def test_create_job():
    response = client.post("/jobs/", json={
        "title": "Backend Developer",
        "company": "TechCorp",
        "location": "Remote",
        "description": "Looking for a Python developer."
    })
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Job created"
    assert "job" in data
    assert data["job"]["title"] == "Backend Developer"

# Test 2: Suscribirse a alertas de empleo
def test_subscribe():
    response = client.post("/subscribe/", json={
        "email": "test@example.com",
        "keyword": "Python"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Subscription successful"
    assert data["subscription"]["email"] == "test@example.com"

# Test 3: Obtener la lista de trabajos (debe devolver al menos uno)
def test_get_jobs():
    response = client.get("/jobs/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0  # Debe haber al menos un trabajo publicado

# Test 4: Buscar trabajos en todas las fuentes
def test_search_jobs():
    response = client.get("/jobs/search/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

# Test 5: Manejar errores al crear un trabajo (campo faltante)
def test_create_job_missing_field():
    response = client.post("/jobs/", json={
        "company": "TechCorp",
        "location": "Remote"
    })
    assert response.status_code == 422  # Error de validación

# Test 6: Manejar errores al suscribirse (email inválido)
def test_subscribe_invalid_email():
    response = client.post("/subscribe/", json={
        "email": "not-an-email",
        "keyword": "Python"
    })
    assert response.status_code == 422  # Error de validación

# Test 7: Enviar alerta cuando se publica un trabajo (simulación)
def test_alert_on_new_job():
    client.post("/subscribe/", json={
        "email": "test@example.com",
        "keyword": "Python"
    })

    response = client.post("/jobs/", json={
        "title": "Python Developer",
        "company": "TechCorp",
        "location": "Remote",
        "description": "Looking for a Python developer."
    })

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Job created"

    # Simular que se enviaría un email
    # En una implementación real, podríamos usar un mock para verificar el envío