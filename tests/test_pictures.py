import os
from io import BytesIO
import pytest
from config import base_dir


def test_add_picture_no_token(client, flat):
    file_name = "fake-text-stream.txt"
    data = {"picture": (BytesIO(b"some initial text data"), file_name)}
    response = client.post("api/v1/flats/1/pictures", data=data)
    response_data = response.get_json()

    assert response.status_code == 401
    alert = "Missing landlord token. Please login or register as landlord."
    assert response_data["message"] == alert
    assert "data" not in response_data


def test_add_picture_tenant_token(client, flat, tenant_token):
    file_name = "fake-text-stream.txt"
    data = {"picture": (BytesIO(b"some initial text data"), file_name)}
    response = client.post(
        "api/v1/flats/1/pictures",
        data=data,
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    response_data = response.get_json()

    assert response.status_code == 401
    assert response_data["message"] == "Only landlord functionality"
    assert "data" not in response_data


def test_add_picture_no_allowed_extension(client, flat, landlord_token):
    file_name = "fake-text-stream.txt"
    data = {"picture": (BytesIO(b"some initial text data"), file_name)}
    response = client.post(
        "api/v1/flats/1/pictures",
        data=data,
        headers={"Authorization": f"Bearer {landlord_token}"},
    )
    response_data = response.get_json()

    assert response.status_code == 415
    assert "data" not in response_data


def test_add_picture_ok(client, flat, landlord_token, file_example):
    with open(file_example["source"], "rb") as img:
        response = client.post(
            "api/v1/flats/1/pictures",
            data={"picture": img, "description": file_example["description"]},
            headers={"Authorization": f"Bearer {landlord_token}"},
        )

    response_data = response.get_json()

    assert response.status_code == 201
    assert response_data["success"] is True
    assert response_data["data"]["name"] == f'flat1_{file_example["name"]}'
    assert response_data["data"]["path"] == file_example["path"]
    assert response_data["data"]["description"] == file_example["description"]


def test_get_all_pictures_no_records(client):
    response = client.get("api/v1/pictures")
    response_data = response.get_json()

    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    assert response_data["success"] is True
    assert response_data["data"] == []


def test_get_all_pictures_sample_data(client, sample_data):
    response = client.get("api/v1/pictures")
    response_data = response.get_json()

    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    assert response_data["success"] is True
    assert len(response_data["data"]) == 2


def test_get_all_flat_pictures(client, sample_data):
    response = client.get("api/v1/flats/1/pictures")
    response_data = response.get_json()

    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    assert response_data["success"] is True
    assert len(response_data["data"]) == 1
    assert response_data["data"][0]["id"] == 1
    assert response_data["data"][0]["flat"]["id"] == 1


def test_get_one_picture(client, sample_data):
    response = client.get("api/v1/pictures/1")
    response_data = response.get_json()

    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    assert response_data["success"] is True
    assert len(response_data["data"]) == 7
    assert response_data["data"]["id"] == 1
    assert response_data["data"]["name"] == "flat1_example.JPG"
    assert response_data["data"]["description"] == "Description for flat1_example.JPG"
    assert response_data["data"]["path"] == os.path.join(
        base_dir, "uploads", "example.JPG"
    )


def test_delete_picture_no_token(client, sample_data):
    response = client.delete("api/v1/pictures/1")
    response_data = response.get_json()

    assert response.status_code == 401
    assert response.headers["Content-Type"] == "application/json"
    assert response_data["success"] is False
    assert "data" not in response_data
    assert (
        response_data["message"]
        == "Missing landlord token. Please login or register as landlord."
    )


def test_delete_picture_tenant_token(client, sample_data, tenant_token):
    response = client.delete(
        "api/v1/pictures/1", headers={"Authorization": f"Bearer {tenant_token}"}
    )
    response_data = response.get_json()

    assert response.status_code == 401
    assert response.headers["Content-Type"] == "application/json"
    assert response_data["success"] is False
    assert "data" not in response_data
    assert response_data["message"] == "Only landlord functionality"


def test_delete_picture_landlord_token(client, sample_data):
    response = client.post(
        "/api/v1/landlords/login",
        json={"identifier": "landlord1", "password": "haslo1"},
    )

    token = response.get_json()["token"]

    assert token

    response = client.delete(
        "api/v1/pictures/1", headers={"Authorization": f"Bearer {token}"}
    )
    response_data = response.get_json()

    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    assert response_data["success"] is True
    assert response_data["data"] == "Picture with id 1 has been deleted"


def test_delete_picture_other_landlord(client, sample_data):
    response = client.post(
        "/api/v1/landlords/login",
        json={"identifier": "landlord2", "password": "haslo2"},
    )
    token = response.get_json()["token"]

    assert token

    response = client.delete(
        "api/v1/pictures/1", headers={"Authorization": f"Bearer {token}"}
    )
    response_data = response.get_json()

    assert response.status_code == 404
    assert response.headers["Content-Type"] == "application/json"
    assert response_data["success"] is False
    assert "data" not in response_data
    assert response_data["message"] == "Picture with id 1 not found"
