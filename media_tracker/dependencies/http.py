import httpx


def get_http_client() -> httpx.Client:
    return httpx.Client(timeout=10.0)