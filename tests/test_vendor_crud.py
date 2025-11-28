from fastapi.testclient import TestClient
from src.main import app
from datetime import datetime, timezone
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

client = TestClient(app)

def test_register_vendor_creates_vendor(client: TestClient):
    payload1 = {"name": "Test1", "category": "supplier"}
    response = client.post("/vendors", json=payload1)

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == payload1["name"]
    assert body["category"] == payload1["category"]
    assert "id" in body
    assert "created_at" in body
    assert "updated_at" in body
    assert body["latest_score"] is None


    payload2 = {"name": "Test1", "category": "LOGISTICS"}
    response = client.post("/vendors", json=payload2)
    
    assert response.status_code == 422


def test_vendor_metric_valid(client: TestClient):
    vendor_payload = {"name": "Test1", "category": "supplier"}
    create_vendor_response = client.post("/vendors", json=vendor_payload)
    
    vendor_data = create_vendor_response.json()
    print(vendor_data)
    vendor_id = vendor_data["id"]
    assert vendor_data["name"] == "Test1"

    metric_payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "on_time_delivery_rate": 92.5,
        "complaint_count": 1,
        "missing_documents": False,
        "compliance_score": 88.0,
    }

    metric_response = client.post(f"/vendors/{vendor_id}/metrics", json=metric_payload)
    assert metric_response.status_code == 201
    metric_data = metric_response.json()
    assert metric_data["vendor_id"] == vendor_id

    vendor_details = client.get(f"/vendors/{vendor_id}")
    assert vendor_details.status_code == 200
    detail_payload = vendor_details.json()
    assert detail_payload["latest_score"] is not None

    scores_response = client.get(f"/vendors/{vendor_id}/scores")
    assert scores_response.status_code == 200
    score_list = scores_response.json()
    assert len(score_list) >= 1


def test_metric_validation_failure(client: TestClient):
    vendor_payload = {"name": "Bad Metrics Inc", "category": "dealer"}
    vendor_id = client.post("/vendors", json=vendor_payload).json()["id"]

    invalid_payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "on_time_delivery_rate": 150,
        "complaint_count": -1,
        "missing_documents": "not-a-bool",
        "compliance_score": 120,
    }
    response = client.post(f"/vendors/{vendor_id}/metrics", json=invalid_payload)
    assert response.status_code == 422
