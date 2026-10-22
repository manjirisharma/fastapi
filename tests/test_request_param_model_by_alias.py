from dirty_equals import IsPartialDict
from fastapi import Cookie, FastAPI, Header, Query
from fastapi.testclient import TestClient
from pydantic import BaseModel, ConfigDict, Field

app = FastAPI()


class Model(BaseModel):
    param: str = Field(alias="param_alias")


@app.get("/query")
async def query_model(data: Model = Query()):
    return {"param": data.param}


@app.get("/header")
async def header_model(data: Model = Header()):
    return {"param": data.param}


@app.get("/cookie")
async def cookie_model(data: Model = Cookie()):
    return {"param": data.param}


def test_query_model_with_alias():
    client = TestClient(app)
    response = client.get("/query", params={"param_alias": "value"})
    assert response.status_code == 200, response.text
    assert response.json() == {"param": "value"}


def test_header_model_with_alias():
    client = TestClient(app)
    response = client.get("/header", headers={"param_alias": "value"})
    assert response.status_code == 200, response.text
    assert response.json() == {"param": "value"}


def test_cookie_model_with_alias():
    client = TestClient(app)
    client.cookies.set("param_alias", "value")
    response = client.get("/cookie")
    assert response.status_code == 200, response.text
    assert response.json() == {"param": "value"}


def test_query_model_with_alias_by_name():
    client = TestClient(app)
    response = client.get("/query", params={"param": "value"})
    assert response.status_code == 422, response.text
    details = response.json()
    assert details["detail"][0]["input"] == {"param": "value"}


def test_header_model_with_alias_by_name():
    client = TestClient(app)
    response = client.get("/header", headers={"param": "value"})
    assert response.status_code == 422, response.text
    details = response.json()
    assert details["detail"][0]["input"] == IsPartialDict({"param": "value"})


def test_cookie_model_with_alias_by_name():
    client = TestClient(app)
    client.cookies.set("param", "value")
    response = client.get("/cookie")
    assert response.status_code == 422, response.text
    details = response.json()
    assert details["detail"][0]["input"] == {"param": "value"}


class PopulateByNameModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    param: str = Field(alias="param_alias")


@app.get("/query-populate-by-name")
async def query_model_populate_by_name(data: PopulateByNameModel = Query()):
    return {"param": data.param}


@app.get("/header-populate-by-name")
async def header_model_populate_by_name(data: PopulateByNameModel = Header()):
    return {"param": data.param}


@app.get("/cookie-populate-by-name")
async def cookie_model_populate_by_name(data: PopulateByNameModel = Cookie()):
    return {"param": data.param}


class ValidateByAliasFalseModel(BaseModel):
    model_config = ConfigDict(validate_by_alias=False)
    param: str = Field(alias="param_alias")


@app.get("/query-validate-by-alias-false")
async def query_model_validate_by_alias_false(
    data: ValidateByAliasFalseModel = Query(),
):
    return {"param": data.param}


@app.get("/header-validate-by-alias-false")
async def header_model_validate_by_alias_false(
    data: ValidateByAliasFalseModel = Header(),
):
    return {"param": data.param}


@app.get("/cookie-validate-by-alias-false")
async def cookie_model_validate_by_alias_false(
    data: ValidateByAliasFalseModel = Cookie(),
):
    return {"param": data.param}


def test_query_model_with_alias_populate_by_name():
    client = TestClient(app)
    response = client.get("/query-populate-by-name", params={"param_alias": "value"})
    assert response.status_code == 200, response.text
    assert response.json() == {"param": "value"}

    response = client.get("/query-populate-by-name", params={"param": "value"})
    assert response.status_code == 200, response.text
    assert response.json() == {"param": "value"}


def test_header_model_with_alias_populate_by_name():
    client = TestClient(app)
    response = client.get("/header-populate-by-name", headers={"param_alias": "value"})
    assert response.status_code == 200, response.text
    assert response.json() == {"param": "value"}

    response = client.get("/header-populate-by-name", headers={"param": "value"})
    assert response.status_code == 200, response.text
    assert response.json() == {"param": "value"}


def test_cookie_model_with_alias_populate_by_name():
    client = TestClient(app)
    client.cookies.set("param_alias", "value")
    response = client.get("/cookie-populate-by-name")
    assert response.status_code == 200, response.text
    assert response.json() == {"param": "value"}

    client.cookies.clear()
    client.cookies.set("param", "value")
    response = client.get("/cookie-populate-by-name")
    assert response.status_code == 200, response.text
    assert response.json() == {"param": "value"}


def test_query_model_with_alias_validate_by_alias_false():
    client = TestClient(app)
    response = client.get("/query-validate-by-alias-false", params={"param": "value"})
    assert response.status_code == 200, response.text
    assert response.json() == {"param": "value"}

    response = client.get(
        "/query-validate-by-alias-false", params={"param_alias": "value"}
    )
    assert response.status_code == 422, response.text


def test_header_model_with_alias_validate_by_alias_false():
    client = TestClient(app)
    response = client.get("/header-validate-by-alias-false", headers={"param": "value"})
    assert response.status_code == 200, response.text
    assert response.json() == {"param": "value"}

    response = client.get(
        "/header-validate-by-alias-false", headers={"param_alias": "value"}
    )
    assert response.status_code == 422, response.text


def test_cookie_model_with_alias_validate_by_alias_false():
    client = TestClient(app)
    client.cookies.set("param", "value")
    response = client.get("/cookie-validate-by-alias-false")
    assert response.status_code == 200, response.text
    assert response.json() == {"param": "value"}

    client.cookies.clear()
    client.cookies.set("param_alias", "value")
    response = client.get("/cookie-validate-by-alias-false")
    assert response.status_code == 422, response.text


def test_openapi_parameter_names_for_alias_configs():
    openapi = app.openapi()
    # Default: alias is param_alias
    assert openapi["paths"]["/query"]["get"]["parameters"][0]["name"] == "param_alias"
    assert openapi["paths"]["/header"]["get"]["parameters"][0]["name"] == "param_alias"
    assert openapi["paths"]["/cookie"]["get"]["parameters"][0]["name"] == "param_alias"

    # populate_by_name: preferred alias is still param_alias
    assert (
        openapi["paths"]["/query-populate-by-name"]["get"]["parameters"][0]["name"]
        == "param_alias"
    )
    assert (
        openapi["paths"]["/header-populate-by-name"]["get"]["parameters"][0]["name"]
        == "param_alias"
    )
    assert (
        openapi["paths"]["/cookie-populate-by-name"]["get"]["parameters"][0]["name"]
        == "param_alias"
    )

    # validate_by_alias=False: param name must be the field name (param)
    assert (
        openapi["paths"]["/query-validate-by-alias-false"]["get"]["parameters"][0][
            "name"
        ]
        == "param"
    )
    assert (
        openapi["paths"]["/header-validate-by-alias-false"]["get"]["parameters"][0][
            "name"
        ]
        == "param"
    )
    assert (
        openapi["paths"]["/cookie-validate-by-alias-false"]["get"]["parameters"][0][
            "name"
        ]
        == "param"
    )
