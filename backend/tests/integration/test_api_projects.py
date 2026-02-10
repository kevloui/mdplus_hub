import pytest
from httpx import AsyncClient


class TestProjectsAPI:
    @pytest.fixture
    async def auth_headers(self, client: AsyncClient) -> dict[str, str]:
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "project@example.com",
                "password": "password123",
                "full_name": "Project User",
            },
        )
        access_token = response.json()["tokens"]["access_token"]
        return {"Authorization": f"Bearer {access_token}"}

    @pytest.mark.asyncio
    async def test_create_project(self, client: AsyncClient, auth_headers: dict):
        response = await client.post(
            "/api/v1/projects/",
            json={
                "name": "Test Project",
                "description": "A test project",
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Project"
        assert data["description"] == "A test project"

    @pytest.mark.asyncio
    async def test_list_projects(self, client: AsyncClient, auth_headers: dict):
        await client.post(
            "/api/v1/projects/",
            json={"name": "Project 1"},
            headers=auth_headers,
        )
        await client.post(
            "/api/v1/projects/",
            json={"name": "Project 2"},
            headers=auth_headers,
        )

        response = await client.get("/api/v1/projects/", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["projects"]) == 2

    @pytest.mark.asyncio
    async def test_get_project(self, client: AsyncClient, auth_headers: dict):
        create_response = await client.post(
            "/api/v1/projects/",
            json={"name": "Get Project"},
            headers=auth_headers,
        )
        project_id = create_response.json()["id"]

        response = await client.get(
            f"/api/v1/projects/{project_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["name"] == "Get Project"
        assert response.json()["molecule_count"] == 0
        assert response.json()["model_count"] == 0

    @pytest.mark.asyncio
    async def test_update_project(self, client: AsyncClient, auth_headers: dict):
        create_response = await client.post(
            "/api/v1/projects/",
            json={"name": "Update Project"},
            headers=auth_headers,
        )
        project_id = create_response.json()["id"]

        response = await client.patch(
            f"/api/v1/projects/{project_id}",
            json={"name": "Updated Name", "description": "New description"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["name"] == "Updated Name"
        assert response.json()["description"] == "New description"

    @pytest.mark.asyncio
    async def test_delete_project(self, client: AsyncClient, auth_headers: dict):
        create_response = await client.post(
            "/api/v1/projects/",
            json={"name": "Delete Project"},
            headers=auth_headers,
        )
        project_id = create_response.json()["id"]

        response = await client.delete(
            f"/api/v1/projects/{project_id}",
            headers=auth_headers,
        )

        assert response.status_code == 204

        get_response = await client.get(
            f"/api/v1/projects/{project_id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_unauthorized_project_access(self, client: AsyncClient):
        response = await client.get("/api/v1/projects/")

        assert response.status_code == 403
