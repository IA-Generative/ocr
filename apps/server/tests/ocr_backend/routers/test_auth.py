import asyncio
from unittest.mock import Mock
from urllib.parse import parse_qs, urlparse

import pytest
from fastapi import HTTPException, Response

from ocr_backend.routers import auth as auth_router


def make_request(cookies: dict | None = None, headers: dict | None = None):
    header_list = []
    if cookies:
        cookie_header = "; ".join(f"{k}={v}" for k, v in cookies.items())
        header_list.append((b"cookie", cookie_header.encode()))
    for key, value in (headers or {}).items():
        header_list.append((key.lower().encode(), value.encode()))
    scope = {"type": "http", "headers": header_list}
    from fastapi import Request

    return Request(scope)


@pytest.fixture(autouse=True)
def patched_settings(monkeypatch):
    monkeypatch.setattr(auth_router._keycloak_settings, "KEYCLOAK_CLIENT_ID", "ocr")
    monkeypatch.setattr(auth_router._keycloak_settings, "KEYCLOAK_REALM", "mirai")
    monkeypatch.setattr(auth_router._keycloak_settings, "KEYCLOAK_PUBLIC_URL", "http://localhost:8080")
    monkeypatch.setattr(auth_router._keycloak_settings, "BACKEND_PUBLIC_URL", "http://localhost:5000")
    monkeypatch.setattr(auth_router._keycloak_settings, "FRONTEND_URL", "http://localhost:8081")
    monkeypatch.setattr(auth_router._keycloak_settings, "SESSION_COOKIE_NAME", "ocr_session")
    monkeypatch.setattr(auth_router._keycloak_settings, "SESSION_COOKIE_SECURE", False)


@pytest.fixture
def fake_store():
    return Mock()


@pytest.fixture(autouse=True)
def patch_session_store(monkeypatch, fake_store):
    monkeypatch.setattr(auth_router, "_session_store", fake_store)
    return fake_store


@pytest.fixture
def fake_openid():
    return Mock()


@pytest.fixture(autouse=True)
def patch_openid(monkeypatch, fake_openid):
    monkeypatch.setattr(auth_router, "_keycloak_openid", fake_openid)
    return fake_openid


async def test_login_redirects_to_keycloak_with_pkce_and_state(fake_store):
    response = await auth_router.login(make_request(), redirect="/tasks/42")

    assert response.status_code == 307
    location = urlparse(response.headers["location"])
    assert location.scheme == "http"
    assert location.netloc == "localhost:8080"
    assert location.path == "/realms/mirai/protocol/openid-connect/auth"

    params = parse_qs(location.query)
    assert params["client_id"] == ["ocr"]
    assert params["redirect_uri"] == ["http://localhost:5000/api/auth/callback"]
    assert params["code_challenge_method"] == ["S256"]
    assert "code_challenge" in params
    assert "state" in params

    (state, code_verifier, next_path), _ = fake_store.save_pending.call_args
    assert next_path == "/tasks/42"
    assert state == params["state"][0]


async def test_login_rejects_unsafe_redirect_and_falls_back_to_root(fake_store):
    _ = await auth_router.login(make_request(), redirect="//evil.tld/phish")

    (_, _, next_path), _ = fake_store.save_pending.call_args
    assert next_path == "/"


async def test_login_rejects_when_rate_limited(fake_store):
    fake_store.check_rate_limit.return_value = False

    with pytest.raises(HTTPException) as exc:
        await auth_router.login(make_request(), redirect="/tasks/42")

    assert exc.value.status_code == 429
    fake_store.save_pending.assert_not_called()


async def test_callback_exchanges_code_and_sets_session_cookie(fake_store, fake_openid):
    fake_store.pop_pending.return_value = Mock(code_verifier="verifier-xyz", next_path="/tasks/42")
    fake_openid.token.return_value = {
        "access_token": "tok",
        "refresh_token": "ref",
        "id_token": "idtok",
        "expires_in": 300,
        "refresh_expires_in": 3600,
    }
    fake_openid.userinfo.return_value = {
        "sub": "user-123",
        "email": "user@example.com",
        "resource_access": {"ocr": {"roles": ["admin"]}},
    }
    fake_store.create.return_value = "new-session-id"

    response = await auth_router.callback(code="auth-code", state="state-abc", error=None)

    fake_openid.token.assert_called_once_with(
        grant_type="authorization_code",
        code="auth-code",
        redirect_uri="http://localhost:5000/api/auth/callback",
        code_verifier="verifier-xyz",
    )
    fake_openid.userinfo.assert_called_once_with("tok")
    assert response.status_code == 302
    assert response.headers["location"] == "http://localhost:8081/tasks/42"
    assert "ocr_session=new-session-id" in response.headers["set-cookie"]
    assert "HttpOnly" in response.headers["set-cookie"]


async def test_callback_rejects_response_without_subject(fake_store, fake_openid):
    fake_store.pop_pending.return_value = Mock(code_verifier="verifier-xyz", next_path="/tasks/42")
    fake_openid.token.return_value = {
        "access_token": "tok",
        "refresh_token": "ref",
        "id_token": "idtok",
        "expires_in": 300,
        "refresh_expires_in": 3600,
    }
    fake_openid.userinfo.return_value = {"active": False}

    response = await auth_router.callback(code="auth-code", state="state-abc", error=None)

    fake_store.create.assert_not_called()
    assert response.status_code == 302
    assert response.headers["location"] == "http://localhost:8081"
    assert "set-cookie" not in response.headers


async def test_callback_without_code_redirects_without_touching_keycloak(fake_store, fake_openid):
    response = await auth_router.callback(code=None, state=None, error="access_denied")

    fake_openid.token.assert_not_called()
    assert response.status_code == 302
    assert response.headers["location"] == "http://localhost:8081"


async def test_callback_rejects_unknown_state(fake_store, fake_openid):
    fake_store.pop_pending.return_value = None

    response = await auth_router.callback(code="auth-code", state="replayed-state", error=None)

    fake_openid.token.assert_not_called()
    assert response.status_code == 302
    assert "set-cookie" not in response.headers


async def test_logout_revokes_refresh_token_and_clears_cookie(fake_store, fake_openid):
    fake_store.get.return_value = Mock(refresh_token="ref-token", id_token="")

    response = Response()
    result = await auth_router.logout(make_request(cookies={"ocr_session": "sid-1"}), response)

    fake_openid.logout.assert_called_once_with("ref-token")
    fake_store.delete.assert_called_once_with("sid-1")
    assert "ocr_session=" in response.headers["set-cookie"]
    assert result["redirectUrl"].startswith("http://localhost:8080/realms/mirai/protocol/openid-connect/logout?")


async def test_logout_redirect_url_hints_the_id_token_when_available(fake_store, fake_openid):
    fake_store.get.return_value = Mock(refresh_token="ref-token", id_token="the-id-token")

    response = Response()
    result = await auth_router.logout(make_request(cookies={"ocr_session": "sid-1"}), response)

    location = urlparse(result["redirectUrl"])
    params = parse_qs(location.query)
    assert params["client_id"] == ["ocr"]
    assert params["post_logout_redirect_uri"] == ["http://localhost:8081"]
    assert params["id_token_hint"] == ["the-id-token"]


async def test_logout_without_cookie_still_returns_a_redirect_url(fake_store, fake_openid):
    response = Response()
    result = await auth_router.logout(make_request(), response)

    fake_store.delete.assert_not_called()
    fake_openid.logout.assert_not_called()
    location = urlparse(result["redirectUrl"])
    params = parse_qs(location.query)
    assert "id_token_hint" not in params


async def test_logout_rejects_cross_site_sec_fetch_site(fake_store, fake_openid):
    response = Response()

    with pytest.raises(HTTPException) as exc:
        await auth_router.logout(
            make_request(
                cookies={"ocr_session": "sid-1"},
                headers={"sec-fetch-site": "cross-site"},
            ),
            response,
        )

    assert exc.value.status_code == 403
    fake_store.delete.assert_not_called()
    fake_openid.logout.assert_not_called()


async def test_logout_rejects_mismatched_origin(fake_store, fake_openid):
    response = Response()

    with pytest.raises(HTTPException) as exc:
        await auth_router.logout(
            make_request(cookies={"ocr_session": "sid-1"}, headers={"origin": "https://evil.tld"}),
            response,
        )

    assert exc.value.status_code == 403
    fake_store.delete.assert_not_called()


async def test_logout_allows_matching_origin(fake_store, fake_openid):
    fake_store.get.return_value = Mock(refresh_token="ref-token", id_token="")
    response = Response()

    await auth_router.logout(
        make_request(
            cookies={"ocr_session": "sid-1"},
            headers={"origin": "http://localhost:8081"},
        ),
        response,
    )

    fake_store.delete.assert_called_once_with("sid-1")


async def test_logout_clears_local_session_even_if_keycloak_revocation_fails(fake_store, fake_openid):
    fake_store.get.return_value = Mock(refresh_token="ref-token", id_token="")
    fake_openid.logout.side_effect = ConnectionError("keycloak unreachable")

    response = Response()
    await auth_router.logout(make_request(cookies={"ocr_session": "sid-1"}), response)

    fake_store.delete.assert_called_once_with("sid-1")


async def test_me_returns_user_profile_shape(fake_store):
    session = Mock(
        user_id="user-123",
        email="user@example.com",
        first_name="Alice",
        last_name="Martin",
        groups=["ocr-users"],
    )
    fake_store.get.return_value = session
    fake_store.ensure_fresh.return_value = session

    result = await auth_router.me(make_request(cookies={"ocr_session": "sid-1"}))

    assert result == {
        "id": "user-123",
        "email": "user@example.com",
        "firstName": "Alice",
        "lastName": "Martin",
        "groups": ["ocr-users"],
    }


async def test_me_refreshes_the_session_off_the_event_loop(fake_store):
    session = Mock(user_id="user-123", email="", first_name="", last_name="", groups=[])
    on_event_loop = []

    def ensure_fresh(sid, current):
        try:
            asyncio.get_running_loop()
            on_event_loop.append(True)
        except RuntimeError:
            on_event_loop.append(False)
        return current

    fake_store.get.return_value = session
    fake_store.ensure_fresh.side_effect = ensure_fresh

    await auth_router.me(make_request(cookies={"ocr_session": "sid-1"}))

    # ensure_fresh may sleep on the refresh lock and calls Keycloak synchronously.
    assert on_event_loop == [False]


async def test_me_without_session_is_unauthorized(fake_store):
    fake_store.get.return_value = None

    with pytest.raises(HTTPException) as exc:
        await auth_router.me(make_request())
    assert exc.value.status_code == 401


async def test_token_exchanges_password_for_access_and_refresh_tokens(fake_openid):
    fake_openid.token.return_value = {
        "access_token": "access-tok",
        "refresh_token": "refresh-tok",
        "expires_in": 300,
    }
    body = auth_router.PasswordGrantRequest(username="user@example.com", password="hunter2")

    result = await auth_router.token(make_request(), body)

    fake_openid.token.assert_called_once_with(
        username="user@example.com",
        password="hunter2",
        scope="openid profile email",
    )
    assert result.access_token == "access-tok"
    assert result.refresh_token == "refresh-tok"
    assert result.expires_in == 300


async def test_token_rejects_invalid_credentials(fake_openid):
    fake_openid.token.side_effect = Exception("invalid_grant")
    body = auth_router.PasswordGrantRequest(username="user@example.com", password="wrong")

    with pytest.raises(HTTPException) as exc:
        await auth_router.token(make_request(), body)
    assert exc.value.status_code == 401


async def test_token_is_rate_limited(fake_store):
    fake_store.check_rate_limit.return_value = False
    body = auth_router.PasswordGrantRequest(username="user@example.com", password="hunter2")

    with pytest.raises(HTTPException) as exc:
        await auth_router.token(make_request(), body)
    assert exc.value.status_code == 429


async def test_refresh_exchanges_refresh_token_for_a_new_pair(fake_openid):
    fake_openid.refresh_token.return_value = {
        "access_token": "new-access-tok",
        "refresh_token": "new-refresh-tok",
        "expires_in": 300,
    }
    body = auth_router.RefreshTokenRequest(refresh_token="old-refresh-tok")

    result = await auth_router.refresh(make_request(), body)

    fake_openid.refresh_token.assert_called_once_with("old-refresh-tok")
    assert result.access_token == "new-access-tok"
    assert result.refresh_token == "new-refresh-tok"


async def test_refresh_rejects_invalid_refresh_token(fake_openid):
    fake_openid.refresh_token.side_effect = Exception("invalid_grant")
    body = auth_router.RefreshTokenRequest(refresh_token="expired")

    with pytest.raises(HTTPException) as exc:
        await auth_router.refresh(make_request(), body)
    assert exc.value.status_code == 401


async def test_refresh_is_rate_limited(fake_store):
    fake_store.check_rate_limit.return_value = False
    body = auth_router.RefreshTokenRequest(refresh_token="tok")

    with pytest.raises(HTTPException) as exc:
        await auth_router.refresh(make_request(), body)
    assert exc.value.status_code == 429
