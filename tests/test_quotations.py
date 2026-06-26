import pytest
from fastapi.testclient import TestClient
import shutil
from pathlib import Path

from app.main import app
from app.routers.quotations import MOCK_FILE_PATH

client = TestClient(app)

@pytest.fixture(autouse=True)
def backup_and_restore_mock_quotes():
    """
    Fixture to backup the mock_quotes.json file before each test and
    restore it after the test finishes. This keeps tests idempotent.
    """
    backup_path = MOCK_FILE_PATH.with_suffix(".json.bak")
    if MOCK_FILE_PATH.exists():
        shutil.copy(MOCK_FILE_PATH, backup_path)
    else:
        backup_path = None

    yield

    if backup_path and backup_path.exists():
        shutil.copy(backup_path, MOCK_FILE_PATH)
        backup_path.unlink()
    elif MOCK_FILE_PATH.exists():
        MOCK_FILE_PATH.unlink()

def test_get_quotations():
    """
    Test GET /quotations returns a 200 status code and a list of quotations.
    """
    response = client.get("/quotations")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    
    # Assert fields are present in the mock data
    if len(data) > 0:
        first_item = data[0]
        assert "rfq_id" in first_item
        assert "items" in first_item
        assert "total_cost" in first_item
        assert "currency" in first_item
        assert "status" in first_item

def test_post_quotation_success():
    """
    Test POST /quotations with a valid RFQ payload returns a 201 created status code,
    creates a new quotation, and correctly calculates the total cost.
    """
    payload = {
        "rfq_id": "RFQ-TEST-999",
        "items": [
            {
                "item_id": "LED-TEST-001",
                "description": "Test Panel Light",
                "quantity": 10,
                "unit_price": 50.0
            },
            {
                "item_id": "LED-TEST-002",
                "description": "Test Driver",
                "quantity": 5,
                "unit_price": 20.0
            }
        ],
        "currency": "EUR"
    }
    
    response = client.post("/quotations", json=payload)
    # The endpoint is designed with status_code=status.HTTP_201_CREATED (201)
    assert response.status_code == 201
    
    data = response.json()
    assert data["rfq_id"] == "RFQ-TEST-999"
    # Expected total: (10 * 50.0) + (5 * 20.0) = 500 + 100 = 600.0
    assert data["total_cost"] == 600.0
    assert data["currency"] == "EUR"
    assert data["status"] == "pending"

    # Verify the new quotation is persisted and returned via GET /quotations
    get_response = client.get("/quotations")
    assert get_response.status_code == 200
    quotes = get_response.json()
    assert any(q["rfq_id"] == "RFQ-TEST-999" for q in quotes)

def test_post_quotation_invalid():
    """
    Test POST /quotations with an invalid payload (missing required fields)
    returns a 422 Unprocessable Entity status code.
    """
    # Missing required field 'items'
    payload = {
        "rfq_id": "RFQ-TEST-888",
        "currency": "USD"
    }
    response = client.post("/quotations", json=payload)
    assert response.status_code == 422
