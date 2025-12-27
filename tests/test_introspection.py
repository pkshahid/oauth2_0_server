def test_introspection_invalid(client):
    response = client.post(
        "/api/oauth/introspect",
        data={"token": "invalid"}
    )
    assert response.json()["active"] is False