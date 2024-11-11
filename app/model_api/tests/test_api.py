from fastapi.testclient import TestClient
from app.api import app

client = TestClient(app)

def test_predict():
    response = client.post("/predict", json={
        "words": [1, 2, 3, 4, 5],
        "features": [[0.1, 0.2], [0.2, 0.3], [0.3, 0.4], [0.4, 0.5], [0.5, 0.6]]
    })
    assert response.status_code == 200
    assert "prediction" in response.json()
