import httpx

TEST_EMAIL = "example@email.com"
TEST_PASSWORD = "12345678"

BASE_URL = "http://localhost:8000"

URL_GET_TOKEN = BASE_URL + "/auth/get_token"
URL_UPDATE_TOKEN = BASE_URL + "/auth/update_token"

URL_SHORTEN = BASE_URL + "/links/shorten"

SHORT_123 = "123"
SHORT_456 = "456"

URL_SHORT_123 = BASE_URL + "/links/" + SHORT_123
URL_SHORT_456 = BASE_URL + "/links/" + SHORT_456

URL_STATS_123 = BASE_URL + "/links/" + SHORT_123 + "/stats"
URL_STATS_456 = BASE_URL + "/links/" + SHORT_456 + "/stats"


def test_get_token():
    url = URL_GET_TOKEN

    data = {"email": TEST_EMAIL, "password": TEST_PASSWORD}

    with httpx.Client() as client:
        response = client.post(url, json=data)

    token = response.json()["token"]

    assert response.status_code == 200
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0


def test_get_token_no_email():
    url = URL_GET_TOKEN

    data = {"email": "", "password": TEST_PASSWORD}

    with httpx.Client() as client:
        response = client.post(url, json=data)

    assert response.status_code == 422


def test_get_token_no_password():
    url = URL_GET_TOKEN

    data = {"email": "unknown@email.com", "password": "shortpw"}

    with httpx.Client() as client:
        response = client.post(url, json=data)

    assert response.status_code == 422


def test_get_token_unauthorized():
    url = URL_GET_TOKEN

    data = {"email": TEST_EMAIL, "password": "wrong_password"}

    with httpx.Client() as client:
        response = client.post(url, json=data)

    assert response.status_code == 401


def test_update_token():
    url = URL_UPDATE_TOKEN

    data = {"email": TEST_EMAIL, "password": TEST_PASSWORD}

    with httpx.Client() as client:
        response = client.post(url, json=data)

    token = response.json()["token"]

    assert response.status_code == 200
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0


def test_update_token_no_email():
    url = URL_UPDATE_TOKEN
    data = {"email": "", "password": TEST_PASSWORD}
    with httpx.Client() as client:
        response = client.post(url, json=data)
    assert response.status_code == 422


def test_update_token_unknown():
    url = URL_UPDATE_TOKEN
    data = {"email": "unknown@email.com", "password": "unknown_password"}
    with httpx.Client() as client:
        response = client.post(url, json=data)
    assert response.status_code == 404


def test_update_token_unauthorized():
    url = URL_UPDATE_TOKEN
    data = {"email": TEST_EMAIL, "password": "wrong_password"}
    with httpx.Client() as client:
        response = client.post(url, json=data)
    assert response.status_code == 401


def get_token():
    url = URL_GET_TOKEN
    data = {"email": TEST_EMAIL, "password": TEST_PASSWORD}
    with httpx.Client() as client:
        response = client.post(url, json=data)
    token = response.json()["token"]
    return token


def test_shorten_link_unauthorized():
    url = URL_SHORTEN
    data = {"original_url": "https://www.google.com"}

    with httpx.Client() as client:
        response = client.post(url, json=data)
    assert response.status_code == 401


def test_shorten_link_authorized():
    token = get_token()
    url = URL_SHORTEN
    headers = {"Authorization": f"Bearer {token}"}
    data = {"original_url": "https://www.google.com"}

    with httpx.Client() as client:
        response = client.post(url, json=data, headers=headers)
    assert response.status_code == 200
    assert (response.json()["original_url"] == "https://www.google.com") or (
        response.json()["original_url"] == "https://www.google.com/"
    )
    assert response.json()["short_url"] is not None
    assert isinstance(response.json()["short_url"], str)
    assert len(response.json()["short_url"]) > 0


def test_delete_link_unauthorized():
    url = URL_SHORT_123

    with httpx.Client() as client:
        response = client.delete(url)
    assert response.status_code == 401


def test_delete_link_authorized():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    try:
        with httpx.Client() as client:
            data = {
                "original_url": "https://www.google.com",
                "short_code": SHORT_123,  # optional
                "expires_at": "2025-12-31T23:59:59",  # optional
            }
            _ = client.post(URL_SHORTEN, json=data, headers=headers)
    except:
        pass
    finally:
        with httpx.Client() as client:
            response = client.delete(URL_SHORT_123, headers=headers)

            assert response.status_code == 200


def test_replace_link_unauthorized():
    url = URL_SHORT_123
    data = {"new_original_url": "https://www.yandex.com"}
    with httpx.Client() as client:
        response = client.put(url, json=data)
    assert response.status_code == 401


def test_replace_link_authorized():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    try:
        with httpx.Client() as client:
            data = {
                "original_url": "https://www.google.com",
                "short_code": SHORT_123,  # optional
                "expires_at": "2025-12-31T23:59:59",  # optional
            }
            _ = client.post(URL_SHORTEN, json=data, headers=headers)
    except:
        pass
    finally:
        with httpx.Client() as client:
            data = {"new_original_url": "https://www.yandex.com"}
            response = client.put(URL_SHORT_123, json=data, headers=headers)
            assert response.status_code == 200
            assert (response.json()["original_url"] == "https://www.yandex.com") or (
                response.json()["original_url"] == "https://www.yandex.com/"
            )
            assert response.json()["short_url"] == URL_SHORT_123


def test_stats_link_unauthorized():
    url = URL_STATS_123
    with httpx.Client() as client:
        response = client.get(url)
    assert response.status_code == 401


def test_stats_link_authorized():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    try:
        with httpx.Client() as client:
            data = {
                "original_url": "https://www.google.com",
                "short_code": SHORT_123,  # optional
                "expires_at": "2025-12-31T23:59:59",  # optional
            }
            _ = client.post(URL_SHORTEN, json=data, headers=headers)
    except:
        pass
    finally:
        with httpx.Client() as client:
            client.get(URL_SHORT_123)
            response = client.get(URL_STATS_123, headers=headers, timeout=30)
            assert response.status_code == 200
