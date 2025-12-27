def test_refresh_token_rotation(client):
    response = client.post(
        "/api/oauth/token",
        data={
            "grant_type": "refresh_token",
            "client_id": "example_client",
            "refresh_token": "invalid"
        }
    )
    assert response.status_code == 400