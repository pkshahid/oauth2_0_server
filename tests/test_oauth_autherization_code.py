def test_authorization_code_flow(client):
    response = client.get(
        "/api/oauth/authorize",
        params={
            "response_type": "code",
            "client_id": "example_client",
            "redirect_uri": "https://app.example.com/callback",
            "scope": "read write"
        },
        allow_redirects=False
    )
    assert response.status_code == 302
    assert "code=" in response.headers["location"]