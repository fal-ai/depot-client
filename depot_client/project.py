from dataclasses import dataclass
from typing import List

import grpc

import depot_client.api.depot.core.v1.project_pb2 as project_pb2
import depot_client.api.depot.core.v1.project_pb2_grpc as project_pb2_grpc


@dataclass
class ProjectInfo:
    project_id: str
    organization_id: str
    name: str
    region_id: str
    # created_at: str
    # hardware: str


class ProjectService:
    def __init__(self, channel: grpc.Channel):
        self.stub = project_pb2_grpc.ProjectServiceStub(channel)

    def list_projects(self) -> List[ProjectInfo]:
        request = project_pb2.ListProjectsRequest()
        response = self.stub.ListProjects(request)
        return [
            ProjectInfo(
                project_id=project.project_id,
                organization_id=project.organization_id,
                name=project.name,
                region_id=project.region_id,
            )
            for project in response.projects
        ]

    def create_project(self, name: str, region_id: str) -> ProjectInfo:
        request = project_pb2.CreateProjectRequest(name=name, region_id=region_id)
        response = self.stub.CreateProject(request)
        return ProjectInfo(
            project_id=response.project.project_id,
            organization_id=response.project.organization_id,
            name=response.project.name,
            region_id=response.project.region_id,
        )

    def update_project(self, project_id: str, name: str, region_id: str) -> ProjectInfo:
        request = project_pb2.UpdateProjectRequest(
            project_id=project_id, name=name, region_id=region_id
        )
        response = self.stub.UpdateProject(request)
        return ProjectInfo(
            project_id=response.project.project_id,
            organization_id=response.project.organization_id,
            name=response.project.name,
            region_id=response.project.region_id,
        )

    def delete_project(self, project_id: str) -> None:
        request = project_pb2.DeleteProjectRequest(project_id=project_id)
        self.stub.DeleteProject(request)

    def reset_project(self, project_id: str) -> None:
        request = project_pb2.ResetProjectRequest(project_id=project_id)
        self.stub.ResetProject(request)

    def list_trust_policies():
        pass

    def add_trust_policy():
        pass

    def remove_trust_policy():
        pass

    def list_tokens():
        pass

    def create_token():
        pass

    def update_token():
        pass

    def delete_token():
        pass


class AsyncProjectService:
    def __init__(self, channel: grpc.Channel):
        self.stub = project_pb2_grpc.ProjectServiceStub(channel)

    async def list_projects(self) -> List[ProjectInfo]:
        request = project_pb2.ListProjectsRequest()
        response = self.stub.ListProjects(request)
        return [
            ProjectInfo(
                project_id=project.project_id,
                organization_id=project.organization_id,
                name=project.name,
                region_id=project.region_id,
            )
            async for project in response.projects
        ]

    async def create_project(self, name: str, region_id: str) -> ProjectInfo:
        request = project_pb2.CreateProjectRequest(name=name, region_id=region_id)
        response = await self.stub.CreateProject(request)
        return ProjectInfo(
            project_id=response.project.project_id,
            organization_id=response.project.organization_id,
            name=response.project.name,
            region_id=response.project.region_id,
        )

    async def update_project(
        self, project_id: str, name: str, region_id: str
    ) -> ProjectInfo:
        request = project_pb2.UpdateProjectRequest(
            project_id=project_id, name=name, region_id=region_id
        )
        response = await self.stub.UpdateProject(request)
        return ProjectInfo(
            project_id=response.project.project_id,
            organization_id=response.project.organization_id,
            name=response.project.name,
            region_id=response.project.region_id,
        )

    async def delete_project(self, project_id: str) -> None:
        request = project_pb2.DeleteProjectRequest(project_id=project_id)
        await self.stub.DeleteProject(request)

    async def reset_project(self, project_id: str) -> None:
        request = project_pb2.ResetProjectRequest(project_id=project_id)
        await self.stub.ResetProject(request)

    async def list_trust_policies():
        pass

    async def add_trust_policy():
        pass

    async def remove_trust_policy():
        pass

    async def list_tokens():
        pass

    async def create_token():
        pass

    async def update_token():
        pass

    async def delete_token():
        pass
