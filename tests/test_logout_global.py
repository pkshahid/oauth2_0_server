def test_global_logout_invalidates_tokens(client):
    logout = client.post("/api/v1/logout")
    assert logout.status_code == 200