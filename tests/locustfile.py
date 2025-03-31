import httpx
from locust import HttpUser, task

# ---------- Get Token ----------
url = "http://localhost:8000/auth/get_token"

data = {"email": "example@email.com", "password": "12345678"}

with httpx.Client() as client:
    response = client.post(url, json=data)

token = response.json()["token"]

try:
    # ---------- Delete short link if exists ----------
    url = "http://localhost:8000/links/loc_test"

    headers = {"Authorization": f"Bearer {token}"}

    with httpx.Client() as client:
        response = client.delete(url, headers=headers)
except:
    pass

# ---------- Shorten URL ----------
url = "http://localhost:8000/links/shorten"

headers = {"Authorization": f"Bearer {token}"}

data = {
    "original_url": "https://www.google.com",
    "short_code": "loc_test",  # optional
    "expires_at": "2025-12-31T23:59:59",  # optional
}

with httpx.Client() as client:
    response = client.post(url, json=data, headers=headers)
    print(response.text)
    original_url = response.json()["original_url"]
    short_url = response.json()["short_url"]


# ---------- Redirect load test ----------
class ShortLinkRedirect(HttpUser):
    host = "http://localhost:8000/links"

    @task
    def redir(self):
        self.client.get("/loc_test")
