import pytest
from httpx import AsyncClient


class TestAuthAPI:
    @pytest.mark.asyncio
    async def test_register_user(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "password123",
                "full_name": "Test User",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["user"]["email"] == "test@example.com"
        assert data["user"]["full_name"] == "Test User"
        assert "access_token" in data["tokens"]
        assert "refresh_token" in data["tokens"]

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient):
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "password123",
                "full_name": "Test User",
            },
        )

        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "password456",
                "full_name": "Another User",
            },
        )

        assert response.status_code == 409
        assert "already registered" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient):
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "login@example.com",
                "password": "password123",
                "full_name": "Login User",
            },
        )

        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "login@example.com",
                "password": "password123",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["user"]["email"] == "login@example.com"
        assert "access_token" in data["tokens"]

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient):
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "wrong@example.com",
                "password": "password123",
                "full_name": "Wrong User",
            },
        )

        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "wrong@example.com",
                "password": "wrongpassword",
            },
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user(self, client: AsyncClient):
        register_response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "me@example.com",
                "password": "password123",
                "full_name": "Me User",
            },
        )
        access_token = register_response.json()["tokens"]["access_token"]

        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200
        assert response.json()["email"] == "me@example.com"

    @pytest.mark.asyncio
    async def test_get_current_user_unauthorized(self, client: AsyncClient):
        response = await client.get("/api/v1/auth/me")

        assert response.status_code == 403
