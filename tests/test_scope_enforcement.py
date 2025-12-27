def test_scope_denied(client):
    response = client.get(
        "/api/admin/users",
        headers={"Authorization": "Bearer invalid"}
    )
    assert response.status_code in (401, 403)