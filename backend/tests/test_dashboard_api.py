import pytest
from unittest.mock import patch
import pandas as pd
from backend.api.app import app

@pytest.fixture(autouse=True)
def mock_dataset():
    with patch('backend.api.app.get_dataset') as mock_get:
        mock_get.return_value = pd.DataFrame({'City': ['Delhi'], 'Datetime': ['2023-01-01'], 'AQI': [100]})
        yield mock_get

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    rv = client.get('/health')
    assert rv.status_code == 200
    json_data = rv.get_json()
    assert json_data['status'] == 'healthy'
    assert 'version' in json_data
    assert 'model' in json_data

def test_dashboard_valid_request(client):
    payload = {
        "city": "Delhi",
        "profile": "General",
        "activity_duration_minutes": 60
    }
    rv = client.post('/api/dashboard', json=payload)
    # The models might not be loaded in test env, so it will fall back to mocked predictions.
    # We should still expect a 200.
    assert rv.status_code == 200
    json_data = rv.get_json()
    assert 'forecastSequence' in json_data
    assert 'health' in json_data
    assert 'activity' in json_data
    assert 'exposureScore' in json_data
    assert 'trend' in json_data

def test_dashboard_missing_city_uses_default(client):
    payload = {
        "profile": "General"
    }
    rv = client.post('/api/dashboard', json=payload)
    assert rv.status_code == 200

def test_dashboard_invalid_profile(client):
    payload = {
        "city": "Delhi",
        "profile": "INVALID_PROFILE_TEST",
        "activity_duration_minutes": 60
    }
    rv = client.post('/api/dashboard', json=payload)
    assert rv.status_code == 400
    json_data = rv.get_json()
    assert json_data['success'] is False
    assert json_data['error']['code'] == 'VALIDATION_ERROR'

def test_dashboard_invalid_duration(client):
    payload = {
        "city": "Delhi",
        "profile": "General",
        "activity_duration_minutes": -5
    }
    rv = client.post('/api/dashboard', json=payload)
    assert rv.status_code == 400
