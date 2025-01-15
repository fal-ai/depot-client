import os
from dataclasses import dataclass
from datetime import datetime
from typing import AsyncIterator, Dict, Iterator, List, Optional, Union

import grpc
import grpc.aio
from google.protobuf.timestamp_pb2 import Timestamp

from depotdev.api.depot.build.v1 import build_pb2, build_pb2_grpc
from depotdev.api.depot.buildkit.v1 import buildkit_pb2, buildkit_pb2_grpc
from depotdev.api.depot.core.v1 import (
    build_pb2 as core_build_pb2,
)
from depotdev.api.depot.core.v1 import (
    build_pb2_grpc as core_build_pb2_grpc,
)
from depotdev.api.depot.core.v1 import (
    project_pb2 as core_project_pb2,
)
from depotdev.api.depot.core.v1 import (
    project_pb2_grpc as core_project_pb2_grpc,
)

DEPOT_DEV_GRPC_HOST = "api.depot.dev"


@dataclass
class BuildEndpoint:
    endpoint: str
    server_name: str
    client_cert: str
    client_key: str
    ca_cert: str


class BaseClient:
    def _create_channel_credentials(self) -> grpc.ChannelCredentials:
        channel_creds = grpc.ssl_channel_credentials()
        token = os.getenv("DEPOT_DEV_API_TOKEN")
        call_creds = grpc.access_token_call_credentials(token)
        return grpc.composite_channel_credentials(channel_creds, call_creds)

    def _proto_to_datetime(self, timestamp: Timestamp) -> datetime:
        return datetime.fromtimestamp(timestamp.seconds + timestamp.nanos / 1e9)

    def _build_to_dict(self, build: core_build_pb2.Build) -> Dict:
        result = {
            "build_id": build.build_id,
            "status": core_build_pb2.Build.Status.Name(build.status),
            "created_at": self._proto_to_datetime(build.created_at),
        }
        for field in ["started_at", "finished_at"]:
            if build.HasField(field):
                result[field] = self._proto_to_datetime(getattr(build, field))
        for field in [
            "build_duration_seconds",
            "saved_duration_seconds",
            "cached_steps",
            "total_steps",
        ]:
            if build.HasField(field):
                result[field] = getattr(build, field)
        return result


class Client(BaseClient):
    def __init__(
        self,
        host: str = DEPOT_DEV_GRPC_HOST,
        port: int = 443,
    ):
        credentials = self._create_channel_credentials()
        self.channel = grpc.secure_channel(f"{host}:{port}", credentials)

        self.build = build_pb2_grpc.BuildServiceStub(self.channel)
        self.buildkit = buildkit_pb2_grpc.BuildKitServiceStub(self.channel)
        self.core_build = core_build_pb2_grpc.BuildServiceStub(self.channel)
        self.core_project = core_project_pb2_grpc.ProjectServiceStub(self.channel)

    def list_projects(self) -> List[Dict]:
        request = core_project_pb2.ListProjectsRequest()
        response = self.core_project.ListProjects(request)
        return [
            {
                "project_id": proj.project_id,
                "organization_id": proj.organization_id,
                "name": proj.name,
                "region_id": proj.region_id,
                "created_at": self._proto_to_datetime(proj.created_at),
                "hardware": core_project_pb2.Hardware.Name(proj.hardware),
            }
            for proj in response.projects
        ]

    def create_build(self, project_id: str) -> tuple[str, str]:
        request = build_pb2.CreateBuildRequest(project_id=project_id)
        response = self.build.CreateBuild(request)
        return response.build_id, response.build_token

    def finish_build(self, build_id: str, error: Optional[str] = None) -> None:
        if error:
            error_msg = build_pb2.FinishBuildRequest.BuildError(error=error)
            request = build_pb2.FinishBuildRequest(build_id=build_id, error=error_msg)
        else:
            success_msg = build_pb2.FinishBuildRequest.BuildSuccess()
            request = build_pb2.FinishBuildRequest(
                build_id=build_id, success=success_msg
            )
        self.build.FinishBuild(request)

    def get_endpoint(
        self, build_id: str, platform: str = "PLATFORM_AMD64"
    ) -> Iterator[BuildEndpoint]:
        platform_enum = buildkit_pb2.Platform.Value(platform)
        request = buildkit_pb2.GetEndpointRequest(
            build_id=build_id, platform=platform_enum
        )

        for response in self.buildkit.GetEndpoint(request):
            if response.HasField("active"):
                active = response.active
                yield BuildEndpoint(
                    endpoint=active.endpoint,
                    server_name=active.server_name,
                    client_cert=active.cert.cert.cert,
                    client_key=active.cert.key.key,
                    ca_cert=active.ca_cert.cert,
                )

    def release_endpoint(self, build_id: str, platform: str = "PLATFORM_AMD64") -> None:
        platform_enum = buildkit_pb2.Platform.Value(platform)
        request = buildkit_pb2.ReleaseEndpointRequest(
            build_id=build_id, platform=platform_enum
        )
        self.buildkit.ReleaseEndpoint(request)

    def share_build(self, build_id: str) -> str:
        request = core_build_pb2.ShareBuildRequest(build_id=build_id)
        response = self.core_build.ShareBuild(request)
        return response.share_url

    def stop_sharing_build(self, build_id: str) -> None:
        request = core_build_pb2.StopSharingBuildRequest(build_id=build_id)
        self.core_build.StopSharingBuild(request)

    def get_build(self, build_id: str) -> Dict:
        request = core_build_pb2.GetBuildRequest(build_id=build_id)
        response = self.core_build.GetBuild(request)
        return self._build_to_dict(response.build)

    def list_builds(
        self,
        project_id: str,
        page_size: Optional[int] = None,
        page_token: Optional[str] = None,
    ) -> tuple[List[Dict], Optional[str]]:
        request = core_build_pb2.ListBuildsRequest(
            project_id=project_id, page_size=page_size, page_token=page_token
        )
        response = self.core_build.ListBuilds(request)
        builds = [self._build_to_dict(build) for build in response.builds]
        return builds, response.next_page_token if response.next_page_token else None

    def close(self):
        self.channel.close()


class AsyncClient(BaseClient):
    def __init__(
        self,
        host: str = DEPOT_DEV_GRPC_HOST,
        port: int = 443,
    ):
        credentials = self._create_channel_credentials()
        self.channel = grpc.aio.secure_channel(f"{host}:{port}", credentials)

        self.build = build_pb2_grpc.BuildServiceStub(self.channel)
        self.buildkit = buildkit_pb2_grpc.BuildKitServiceStub(self.channel)
        self.core_build = core_build_pb2_grpc.BuildServiceStub(self.channel)
        self.core_project = core_project_pb2_grpc.ProjectServiceStub(self.channel)

    async def list_projects(self) -> List[Dict]:
        request = core_project_pb2.ListProjectsRequest()
        response = await self.core_project.ListProjects(request)
        return [
            {
                "project_id": proj.project_id,
                "organization_id": proj.organization_id,
                "name": proj.name,
                "region_id": proj.region_id,
                "created_at": self._proto_to_datetime(proj.created_at),
                "hardware": core_project_pb2.Hardware.Name(proj.hardware),
            }
            for proj in response.projects
        ]

    async def create_build(self, project_id: str) -> tuple[str, str]:
        request = build_pb2.CreateBuildRequest(project_id=project_id)
        response = await self.build.CreateBuild(request)
        return response.build_id, response.build_token

    async def finish_build(self, build_id: str, error: Optional[str] = None) -> None:
        if error:
            error_msg = build_pb2.FinishBuildRequest.BuildError(error=error)
            request = build_pb2.FinishBuildRequest(build_id=build_id, error=error_msg)
        else:
            success_msg = build_pb2.FinishBuildRequest.BuildSuccess()
            request = build_pb2.FinishBuildRequest(
                build_id=build_id, success=success_msg
            )
        await self.build.FinishBuild(request)

    async def get_endpoint(
        self, build_id: str, platform: str = "PLATFORM_AMD64"
    ) -> AsyncIterator[BuildEndpoint]:
        platform_enum = buildkit_pb2.Platform.Value(platform)
        request = buildkit_pb2.GetEndpointRequest(
            build_id=build_id, platform=platform_enum
        )

        async for response in self.buildkit.GetEndpoint(request):
            if response.HasField("active"):
                active = response.active
                yield BuildEndpoint(
                    endpoint=active.endpoint,
                    server_name=active.server_name,
                    client_cert=active.cert.cert.cert,
                    client_key=active.cert.key.key,
                    ca_cert=active.ca_cert.cert,
                )

    async def release_endpoint(
        self, build_id: str, platform: str = "PLATFORM_AMD64"
    ) -> None:
        platform_enum = buildkit_pb2.Platform.Value(platform)
        request = buildkit_pb2.ReleaseEndpointRequest(
            build_id=build_id, platform=platform_enum
        )
        await self.buildkit.ReleaseEndpoint(request)

    async def share_build(self, build_id: str) -> str:
        request = core_build_pb2.ShareBuildRequest(build_id=build_id)
        response = await self.core_build.ShareBuild(request)
        return response.share_url

    async def stop_sharing_build(self, build_id: str) -> None:
        request = core_build_pb2.StopSharingBuildRequest(build_id=build_id)
        await self.core_build.StopSharingBuild(request)

    async def get_build(self, build_id: str) -> Dict:
        request = core_build_pb2.GetBuildRequest(build_id=build_id)
        response = await self.core_build.GetBuild(request)
        return self._build_to_dict(response.build)

    async def list_builds(
        self,
        project_id: str,
        page_size: Optional[int] = None,
        page_token: Optional[str] = None,
    ) -> tuple[List[Dict], Optional[str]]:
        request = core_build_pb2.ListBuildsRequest(
            project_id=project_id, page_size=page_size, page_token=page_token
        )
        response = await self.core_build.ListBuilds(request)
        builds = [self._build_to_dict(build) for build in response.builds]
        return builds, response.next_page_token if response.next_page_token else None

    async def close(self):
        await self.channel.close()


if __name__ == "__main__":
    client = Client()
    print(client.list_projects())
    print(client.list_builds("749dxclhrj"))
    client.close()
