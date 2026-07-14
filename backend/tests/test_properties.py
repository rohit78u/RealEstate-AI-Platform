def test_list_properties_empty(client):
    response = client.get("/api/properties")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []


def test_admin_create_property(client, auth_headers):
    create = client.post(
        "/api/properties",
        json={
            "title": "Test Home",
            "description": "A test property",
            "price": 5000000,
            "bedrooms": 2,
            "bathrooms": 2,
            "area_sqft": 1000,
            "floors": 1,
            "year_built": 2020,
            "parking": 1,
            "city": "Mumbai",
            "location": "Andheri",
        },
        headers=auth_headers,
    )
    assert create.status_code == 403

    client.post(
        "/api/auth/register",
        json={"email": "admin@test.com", "password": "adminpass", "full_name": "Admin"},
    )
