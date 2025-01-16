import os
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

import grpc
import grpc.aio
from google.protobuf.timestamp_pb2 import Timestamp

from depot_client.build import AsyncBuildService, BuildService
from depot_client.buildkit import AsyncBuildKitService, BuildKitService, EndpointInfo
from depot_client.core_build import AsyncCoreBuildService, BuildInfo, CoreBuildService
from depot_client.project import AsyncProjectService, ProjectInfo, ProjectService

DEPOT_GRPC_HOST = "api.depot.dev"
DEPOT_GRPC_PORT = 443


@dataclass
class Endpoint(EndpointInfo):
    build_id: str
    platform: str
    buildkit: BuildKitService

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        self.buildkit.release_endpoint(self.build_id, self.platform)


@dataclass
class AsyncEndpoint(EndpointInfo):
    build_id: str
    platform: str
    buildkit: BuildKitService

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()

    async def close(self):
        await self.buildkit.release_endpoint(self.build_id, self.platform)


class Build:
    def __init__(self, build_service, build_id: str, build_token: str):
        self.build_id = build_id
        self.build_token = build_token
        self.buildkit = BuildKitService(build_token)

    def close(self):
        self.buildkit.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def get_endpoint(self, platform: Optional[str] = None) -> Endpoint:
        endpoint = self.buildkit.get_endpoint(self.build_id, platform=platform)
        return Endpoint(
            endpoint=endpoint.endpoint,
            server_name=endpoint.server_name,
            cert=endpoint.cert,
            key=endpoint.key,
            ca_cert=endpoint.ca_cert,
            build_id=self.build_id,
            platform=platform,
            buildkit=self.buildkit,
        )


class AsyncBuild:
    def __init__(self, build_service, build_id: str, build_token: str):
        self.build_id = build_id
        self.build_token = build_token
        self.buildkit = AsyncBuildKitService(build_token)

    async def close(self):
        await self.buildkit.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()

    async def get_endpoint(self, platform: Optional[str] = None) -> AsyncEndpoint:
        endpoint = await self.buildkit.get_endpoint(self.build_id, platform=platform)
        return AsyncEndpoint(
            endpoint=endpoint.endpoint,
            server_name=endpoint.server_name,
            cert=endpoint.cert,
            key=endpoint.key,
            ca_cert=endpoint.ca_cert,
            build_id=self.build_id,
            platform=platform,
            buildkit=self.buildkit,
        )


class BaseClient:
    def _create_channel_credentials(self) -> grpc.ChannelCredentials:
        channel_creds = grpc.ssl_channel_credentials()
        token = os.getenv("DEPOT_API_TOKEN")
        call_creds = grpc.access_token_call_credentials(token)
        return grpc.composite_channel_credentials(channel_creds, call_creds)

    def _proto_to_datetime(self, timestamp: Timestamp) -> datetime:
        return datetime.fromtimestamp(timestamp.seconds + timestamp.nanos / 1e9)


class Client(BaseClient):
    def __init__(
        self,
        host: str = DEPOT_GRPC_HOST,
        port: int = DEPOT_GRPC_PORT,
    ):
        credentials = self._create_channel_credentials()
        self.channel = grpc.secure_channel(f"{host}:{port}", credentials)
        self.build = BuildService(self.channel)
        self.core_build = CoreBuildService(self.channel)
        self.project = ProjectService(self.channel)

    def close(self):
        self.channel.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def list_projects(self) -> List[ProjectInfo]:
        return self.project.list_projects()

    def create_build(self, project_id: str) -> Build:
        build_id, build_token = self.build.create_build(project_id)
        return Build(self.build, build_id=build_id, build_token=build_token)

    def finish_build(self, build_id: str, error: Optional[str] = None) -> None:
        return self.build.finish_build(build_id, error=error)

    def share_build(self, build_id: str) -> str:
        return self.core_build.share_build(build_id)

    def stop_sharing_build(self, build_id: str) -> None:
        return self.core_build.stop_sharing_build(build_id)

    def get_build(self, build_id: str) -> BuildInfo:
        return self.core_build.get_build(build_id)

    def list_builds(
        self,
        project_id: str,
    ) -> List[BuildInfo]:
        return self.core_build.list_builds(project_id)

    def create_endpoint(
        self, build_id: str, platform: Optional[str] = None
    ) -> Endpoint:
        return self.buildkit.create_endpoint(build_id, platform)


class AsyncClient(BaseClient):
    def __init__(
        self,
        host: str = DEPOT_GRPC_HOST,
        port: int = DEPOT_GRPC_PORT,
    ):
        credentials = self._create_channel_credentials()
        self.channel = grpc.aio.secure_channel(f"{host}:{port}", credentials)
        self.build = AsyncBuildService(self.channel)
        self.core_build = AsyncCoreBuildService(self.channel)
        self.project = AsyncProjectService(self.channel)

    async def close(self):
        await self.channel.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()

    async def list_projects(self) -> List[ProjectInfo]:
        return await self.project.list_projects()

    async def create_build(self, project_id: str) -> AsyncBuild:
        build_id, build_token = await self.build.create_build(project_id)
        return AsyncBuild(self.build, build_id=build_id, build_token=build_token)

    async def finish_build(self, build_id: str, error: Optional[str] = None) -> None:
        return await self.build.finish_build(build_id, error=error)

    async def share_build(self, build_id: str) -> str:
        return await self.core_build.share_build(build_id)

    async def stop_sharing_build(self, build_id: str) -> None:
        return await self.core_build.stop_sharing_build(build_id)

    async def get_build(self, build_id: str) -> BuildInfo:
        return await self.core_build.get_build(build_id)

    async def list_builds(
        self,
        project_id: str,
    ) -> List[BuildInfo]:
        return await self.core_build.list_builds(project_id)


def _main():
    with Client() as client:
        client.list_projects()
        project_id = "749dxclhrj"
        client.list_builds(project_id)
        with client.create_build(project_id) as build:
            with build.get_endpoint() as endpoint:
                print(repr(endpoint))


async def _async_main():
    async with AsyncClient() as client:
        await client.list_projects()
        project_id = "749dxclhrj"
        await client.list_builds(project_id)
        async with await client.create_build(project_id) as build:
            async with await build.get_endpoint() as endpoint:
                print(repr(endpoint))


if __name__ == "__main__":
    _main()
    import asyncio

    asyncio.run(_async_main())
