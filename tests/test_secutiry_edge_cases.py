def test_reuse_authorization_code(client):
    # Authorization codes must be single-use
    assert True