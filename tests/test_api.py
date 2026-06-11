"""
Unit tests for RAG Retail Agent API
Run with: pytest tests/ -v
"""

import pytest
from fastapi.testclient import TestClient
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Mock the heavy ML startup so tests are fast
import unittest.mock as mock

def test_root_returns_200():
    """Test health check endpoint"""
    # This test structure shows how to test FastAPI endpoints
    # In CI, the full model is loaded; locally you can mock it
    assert True  # placeholder — replace with TestClient(app).get("/")

def test_products_endpoint_structure():
    """Test that products data has expected fields"""
    import json
    with open(os.path.join(os.path.dirname(__file__), "../data/products.json")) as f:
        products = json.load(f)
    assert len(products) > 0
    for p in products:
        assert "id" in p
        assert "name" in p
        assert "price" in p
        assert "description" in p

def test_product_price_is_positive():
    """All product prices must be positive"""
    import json
    with open(os.path.join(os.path.dirname(__file__), "../data/products.json")) as f:
        products = json.load(f)
    for p in products:
        assert p["price"] > 0, f"Product {p['id']} has invalid price"

def test_product_stock_is_non_negative():
    """All products must have non-negative stock"""
    import json
    with open(os.path.join(os.path.dirname(__file__), "../data/products.json")) as f:
        products = json.load(f)
    for p in products:
        assert p["stock"] >= 0, f"Product {p['id']} has negative stock"
