def test_token_exchange(client):
    token_resp = client.post(
        "/api/oauth/token",
        data={
            "grant_type": "client_credentials",
            "client_id": "example_client",
            "client_secret": "secret",
            "scope": "read"
        }
    )
    assert token_resp.status_code == 200
    assert "access_token" in token_resp.json()