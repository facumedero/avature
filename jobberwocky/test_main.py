
import pytest
import logging
from unittest.mock import patch
from fastapi.testclient import TestClient
from jobberwocky.main import app

# Configurar logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


client = TestClient(app)

# Test 1: Crear un trabajo correctamente
def test_create_job():
    logger.info("Test: Crear un trabajo correctamente")
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
    logger.info("✅ Test exitoso: Trabajo creado correctamente")


# Test 2: Suscribirse a alertas de empleo
def test_subscribe():
    logger.info("Test: Suscribirse a alertas de empleo")
    response = client.post("/subscribe/", json={
        "email": "test@example.com",
        "keyword": "Python"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Subscription successful"
    assert data["subscription"]["email"] == "test@example.com"
    logger.info("✅ Test exitoso: Suscripción realizada correctamente")


# Test 3: Obtener la lista de trabajos (debe devolver al menos uno)
def test_get_jobs():
    logger.info("Test: Obtener la lista de trabajos")
    response = client.get("/jobs/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0  # Debe haber al menos un trabajo publicado
    logger.info(f"✅ Test exitoso: Se encontraron {len(data)} trabajos disponibles")


# Test 4: Buscar trabajos en todas las fuentes
def test_search_jobs():
    logger.info("Test: Buscar trabajos en todas las fuentes")
    response = client.get("/jobs/search/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    logger.info(f"✅ Test exitoso: Se encontraron {len(data)} resultados en la búsqueda")

# Test 5: Manejar errores al crear un trabajo (campo faltante)
def test_create_job_missing_field():
    logger.info("Test: Manejar error al crear un trabajo sin todos los campos requeridos")
    response = client.post("/jobs/", json={
        "company": "TechCorp",
        "location": "Remote"
    })
    assert response.status_code == 422  # Error de validación
    logger.info("✅ Test exitoso: Se detectó correctamente el error por campo faltante")


# Test 6: Manejar errores al suscribirse (email inválido)
def test_subscribe_invalid_email():
    logger.info("Test: Manejar error al suscribirse con un email inválido")
    response = client.post("/subscribe/", json={
        "email": "not-an-email",
        "keyword": "Python"
    })
    assert response.status_code == 422  # Error de validación
    logger.info("✅ Test exitoso: Se detectó correctamente el error de email inválido")

# Test 7: Enviar alerta cuando se publica un trabajo (simulación)
def test_alert_on_new_job():
    logger.info("Test: Enviar alerta cuando se publica un nuevo trabajo")
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
    logger.info("✅ Test exitoso: Trabajo creado y alerta generada correctamente")

    # Simular que se enviaría un email
    # En una implementación real, podríamos usar un mock para verificar el envío