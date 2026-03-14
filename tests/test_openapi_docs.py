from app import create_app


def _client():
    app = create_app()
    app.config.update(TESTING=True)
    return app.test_client()


def test_swagger_ui_is_available():
    client = _client()

    response = client.get("/docs/")

    assert response.status_code == 200
    assert b"swagger-ui" in response.data.lower() or b"swagger" in response.data.lower()


def test_openapi_spec_exposes_registered_api_contract():
    client = _client()

    response = client.get("/openapi.json")
    spec = response.get_json()

    assert response.status_code == 200
    assert spec["swagger"] == "2.0"
    assert "/pessoas" in spec["paths"]
    assert "/atendimentos/{id}" in spec["paths"]
    assert "/prontuarios/{id}" in spec["paths"]
    assert "/encaminhamentos/{encaminhamento_id}/status" in spec["paths"]
    assert "ErrorResponse" in spec["definitions"]
