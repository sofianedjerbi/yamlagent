"""Tests for the Flask application."""

import json

import pytest

from calc3d.app import app


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestFlaskApp:
    """Test cases for Flask application endpoints."""

    # ============ Index Route Tests ============

    def test_index_returns_200(self, client):
        """Test index page returns successfully."""
        response = client.get('/')
        assert response.status_code == 200

    def test_index_returns_html(self, client):
        """Test index page returns HTML content."""
        response = client.get('/')
        assert b'<!DOCTYPE html>' in response.data or b'<html' in response.data

    # ============ Calculate Endpoint - Happy Path ============

    def test_calculate_simple_addition(self, client):
        """Test simple addition calculation."""
        response = client.post(
            '/calculate',
            data=json.dumps({'expression': '2 + 3'}),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['result'] == 5

    def test_calculate_multiplication(self, client):
        """Test multiplication calculation."""
        response = client.post(
            '/calculate',
            data=json.dumps({'expression': '6 * 7'}),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['result'] == 42

    def test_calculate_complex_expression(self, client):
        """Test complex expression calculation."""
        response = client.post(
            '/calculate',
            data=json.dumps({'expression': '(10 + 5) * 2'}),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['result'] == 30

    def test_calculate_with_power(self, client):
        """Test power operation."""
        response = client.post(
            '/calculate',
            data=json.dumps({'expression': '2**3'}),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['result'] == 8

    # ============ Calculate Endpoint - Edge Cases ============

    def test_calculate_decimal_numbers(self, client):
        """Test calculation with decimal numbers."""
        response = client.post(
            '/calculate',
            data=json.dumps({'expression': '3.5 + 2.5'}),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['result'] == 6.0

    def test_calculate_negative_numbers(self, client):
        """Test calculation with negative numbers."""
        response = client.post(
            '/calculate',
            data=json.dumps({'expression': '-5 + 3'}),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['result'] == -2

    def test_calculate_expression_with_spaces(self, client):
        """Test calculation with extra spaces."""
        response = client.post(
            '/calculate',
            data=json.dumps({'expression': '  2  +  3  '}),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['result'] == 5

    # ============ Calculate Endpoint - Error Cases ============

    def test_calculate_division_by_zero(self, client):
        """Test division by zero returns error in result."""
        response = client.post(
            '/calculate',
            data=json.dumps({'expression': '10 / 0'}),
            content_type='application/json'
        )
        # App returns 200 with error message in result field
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'result' in data
        assert isinstance(data['result'], str)
        assert 'zero' in data['result'].lower()

    def test_calculate_invalid_expression(self, client):
        """Test invalid expression returns error in result."""
        response = client.post(
            '/calculate',
            data=json.dumps({'expression': '2 + abc'}),
            content_type='application/json'
        )
        # App returns 200 with error message in result field
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'result' in data
        assert isinstance(data['result'], str)
        assert 'Invalid' in data['result'] or 'Error' in data['result']

    def test_calculate_empty_expression(self, client):
        """Test empty expression returns error."""
        response = client.post(
            '/calculate',
            data=json.dumps({'expression': ''}),
            content_type='application/json'
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_calculate_no_expression_field(self, client):
        """Test missing expression field returns error."""
        response = client.post(
            '/calculate',
            data=json.dumps({}),
            content_type='application/json'
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_calculate_no_json_data(self, client):
        """Test no JSON data returns error."""
        response = client.post('/calculate')
        # Flask returns 415 Unsupported Media Type when no content-type is set
        assert response.status_code in [400, 415]
        if response.status_code == 400:
            data = json.loads(response.data)
            assert 'error' in data

    def test_calculate_invalid_json(self, client):
        """Test invalid JSON returns error."""
        response = client.post(
            '/calculate',
            data='invalid json',
            content_type='application/json'
        )
        assert response.status_code == 400

    # ============ HTTP Method Tests ============

    def test_calculate_get_not_allowed(self, client):
        """Test GET method is not allowed on /calculate."""
        response = client.get('/calculate')
        assert response.status_code == 405  # Method Not Allowed

    def test_calculate_put_not_allowed(self, client):
        """Test PUT method is not allowed on /calculate."""
        response = client.put(
            '/calculate',
            data=json.dumps({'expression': '2 + 3'}),
            content_type='application/json'
        )
        assert response.status_code == 405

    # ============ Content Type Tests ============

    def test_calculate_without_content_type(self, client):
        """Test request without proper content type."""
        response = client.post(
            '/calculate',
            data=json.dumps({'expression': '2 + 3'})
        )
        # Flask returns 415 when content-type is not application/json
        assert response.status_code in [200, 400, 415]

    # ============ Security Tests ============

    def test_calculate_prevents_code_injection(self, client):
        """Test that code injection attempts are blocked."""
        response = client.post(
            '/calculate',
            data=json.dumps({'expression': "__import__('os').system('ls')"}),
            content_type='application/json'
        )
        # Returns 200 with "Invalid characters" message in result
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'result' in data
        assert isinstance(data['result'], str)
        assert 'Invalid' in data['result']

    # ============ Additional Edge Cases ============

    def test_calculate_very_long_expression(self, client):
        """Test handling of very long expression."""
        long_expr = " + ".join(["1"] * 100)
        response = client.post(
            '/calculate',
            data=json.dumps({'expression': long_expr}),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['result'] == 100

    def test_calculate_nested_operations(self, client):
        """Test deeply nested operations."""
        response = client.post(
            '/calculate',
            data=json.dumps({'expression': '((((1 + 1) * 2) + 3) * 2)'}),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['result'] == 14

    def test_calculate_with_whitespace_expression(self, client):
        """Test whitespace-only expression field."""
        response = client.post(
            '/calculate',
            data=json.dumps({'expression': '   '}),
            content_type='application/json'
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_calculate_with_zero_result(self, client):
        """Test calculation resulting in zero."""
        response = client.post(
            '/calculate',
            data=json.dumps({'expression': '5 - 5'}),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['result'] == 0

    def test_calculate_with_negative_result(self, client):
        """Test calculation resulting in negative number."""
        response = client.post(
            '/calculate',
            data=json.dumps({'expression': '10 - 20'}),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['result'] == -10

    def test_calculate_extra_json_fields(self, client):
        """Test request with extra JSON fields."""
        response = client.post(
            '/calculate',
            data=json.dumps({'expression': '2 + 2', 'extra': 'ignored'}),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['result'] == 4
