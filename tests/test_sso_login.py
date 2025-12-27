def test_login_success(client):
    response = client.post(
        "/api/v1/sso/login",
        data={"email": "test@example.com", "password": "password"}
    )
    assert response.status_code in (200, 302)
    assert "sso_session" in response.cookies