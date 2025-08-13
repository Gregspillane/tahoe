"""Basic API tests for agent-engine service"""

import pytest
import json
import os
from fastapi.testclient import TestClient
from datetime import datetime


# Set test environment variables
os.environ["SERVICE_TOKEN"] = "test-token-123"
os.environ["DATABASE_URL"] = "postgresql://tahoe:tahoe@localhost:5435/tahoe"
os.environ["REDIS_URL"] = "redis://localhost:6382"
os.environ["ENVIRONMENT"] = "test"


from src.main import app


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Get authorization headers"""
    return {"Authorization": "Bearer test-token-123"}


@pytest.fixture
def sample_interaction():
    """Load sample interaction fixture"""
    fixture_path = os.path.join(
        os.path.dirname(__file__),
        "fixtures",
        "sample_interaction.json"
    )
    with open(fixture_path, "r") as f:
        return json.load(f)


# Health Check Tests
def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code in [200, 503]  # May be degraded on first run
    data = response.json()
    assert "service" in data
    assert "status" in data
    assert "version" in data
    assert "dependencies" in data


def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "agent-engine"
    assert "version" in data
    assert "docs" in data


# Authentication Tests
def test_auth_required(client):
    """Test that authentication is required for protected endpoints"""
    response = client.get("/agents/templates")
    assert response.status_code == 403  # No auth header


def test_invalid_token(client):
    """Test invalid token is rejected"""
    headers = {"Authorization": "Bearer invalid-token"}
    response = client.get("/agents/templates", headers=headers)
    assert response.status_code == 401


def test_valid_token(client, auth_headers):
    """Test valid token is accepted"""
    response = client.get("/agents/templates", headers=auth_headers)
    assert response.status_code == 200


# Analysis Endpoint Tests
def test_analyze_endpoint(client, auth_headers, sample_interaction):
    """Test POST /analyze endpoint"""
    request_data = {
        "interaction": sample_interaction,
        "scorecard_id": "test-scorecard-001",
        "portfolio_id": "test-portfolio-001",
        "options": {}
    }
    
    response = client.post(
        "/analyze",
        json=request_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "analysis_id" in data
    assert "status" in data
    assert "overall_score" in data
    assert data["status"] == "complete"  # Mock returns complete


def test_get_analysis(client, auth_headers, sample_interaction):
    """Test GET /analysis/{id} endpoint"""
    # First create an analysis
    request_data = {
        "interaction": sample_interaction,
        "scorecard_id": "test-scorecard-001",
        "portfolio_id": "test-portfolio-001"
    }
    
    create_response = client.post(
        "/analyze",
        json=request_data,
        headers=auth_headers
    )
    analysis_id = create_response.json()["analysis_id"]
    
    # Now retrieve it
    response = client.get(
        f"/analysis/{analysis_id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["analysis_id"] == analysis_id
    assert "status" in data
    assert "overall_score" in data


def test_analysis_status(client, auth_headers, sample_interaction):
    """Test GET /status/analysis/{id} endpoint"""
    # First create an analysis
    request_data = {
        "interaction": sample_interaction,
        "scorecard_id": "test-scorecard-001",
        "portfolio_id": "test-portfolio-001"
    }
    
    create_response = client.post(
        "/analyze",
        json=request_data,
        headers=auth_headers
    )
    analysis_id = create_response.json()["analysis_id"]
    
    # Get status
    response = client.get(
        f"/status/analysis/{analysis_id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["analysis_id"] == analysis_id
    assert "status" in data
    assert "phase" in data


# Agent Template Tests
def test_list_agent_templates(client, auth_headers):
    """Test GET /agents/templates endpoint"""
    response = client.get("/agents/templates", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_create_agent_template(client, auth_headers):
    """Test POST /agents/templates endpoint"""
    template_data = {
        "name": f"test_agent_{datetime.now().timestamp()}",
        "type": "specialist",
        "model": "gemini-2.0-flash",
        "description": "Test agent template",
        "capabilities": ["test_capability"],
        "tools": [],
        "modelConfig": {"temperature": 0.3},
        "triggerRules": {}
    }
    
    response = client.post(
        "/agents/templates",
        json=template_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == template_data["name"]
    assert data["type"] == template_data["type"]


# Scorecard Tests
def test_list_scorecards(client, auth_headers):
    """Test GET /scorecards endpoint"""
    response = client.get("/scorecards", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_create_scorecard(client, auth_headers):
    """Test POST /scorecards endpoint"""
    # First ensure we have a portfolio
    from src.models.database import database_manager
    import asyncio
    
    async def create_test_portfolio():
        await database_manager.connect()
        db = database_manager.get_client()
        portfolio = await db.portfolio.create({
            "data": {
                "organizationId": "test-org-001",
                "name": "Test Portfolio",
                "configuration": {}
            }
        })
        return portfolio.id
    
    portfolio_id = asyncio.run(create_test_portfolio())
    
    scorecard_data = {
        "name": f"test_scorecard_{datetime.now().timestamp()}",
        "portfolioId": portfolio_id,
        "description": "Test scorecard",
        "requirements": {},
        "thresholds": {"pass": 80, "fail": 50},
        "aggregationRules": {}
    }
    
    response = client.post(
        "/scorecards",
        json=scorecard_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == scorecard_data["name"]


# Metrics Test
def test_metrics_endpoint(client):
    """Test GET /metrics endpoint"""
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "requests_total" in data
    assert "average_response_time" in data
    assert "errors_total" in data


# Error Handling Tests
def test_404_analysis(client, auth_headers):
    """Test 404 for non-existent analysis"""
    response = client.get(
        "/analysis/non-existent-id",
        headers=auth_headers
    )
    assert response.status_code == 404


def test_invalid_request_data(client, auth_headers):
    """Test invalid request data returns 422"""
    invalid_data = {
        "interaction": "not-an-object",  # Should be object
        "scorecard_id": "test"
    }
    
    response = client.post(
        "/analyze",
        json=invalid_data,
        headers=auth_headers
    )
    assert response.status_code == 422  # Validation error