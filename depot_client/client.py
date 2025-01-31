import asyncio
import os
import threading
import time
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass
from datetime import datetime
from typing import AsyncIterator, Iterator, List, Optional

import grpc
import grpc.aio
from google.protobuf.timestamp_pb2 import Timestamp

from depot_client.build import AsyncBuildService, BuildService
from depot_client.buildkit import AsyncBuildKitService, BuildKitService, EndpointInfo
from depot_client.core_build import AsyncCoreBuildService, BuildInfo, CoreBuildService
from depot_client.project import AsyncProjectService, ProjectInfo, ProjectService

DEPOT_GRPC_HOST = "api.depot.dev"
DEPOT_GRPC_PORT = 443

REPORT_HEALTH_INTERVAL = 60
REPORT_HEALTH_THREAD_CANCEL_TIMEOUT = 0.1


@dataclass
class Endpoint(EndpointInfo):
    build_id: str
    platform: str
    buildkit: BuildKitService

    def _report_health(self):
        while not self._stop_health.is_set():
            self.buildkit.report_health(self.build_id, self.platform)
            time.sleep(REPORT_HEALTH_INTERVAL)

    def __enter__(self):
        self._health_thread = threading.Thread(target=self._report_health, daemon=True)
        self._stop_health = threading.Event()
        self._health_thread.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._stop_health.set()
        self._health_thread.join(timeout=REPORT_HEALTH_THREAD_CANCEL_TIMEOUT)
        self.close()

    def close(self):
        self.buildkit.release_endpoint(self.build_id, self.platform)


@dataclass
class AsyncEndpoint(EndpointInfo):
    build_id: str
    platform: str
    buildkit: BuildKitService

    async def _report_health(self):
        while True:
            await self.buildkit.report_health(self.build_id, self.platform)
            await asyncio.sleep(REPORT_HEALTH_INTERVAL)

    async def __aenter__(self):
        self._health_task = asyncio.create_task(self._report_health())
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        self._health_task.cancel()
        await self.close()

    async def close(self):
        await self.buildkit.release_endpoint(self.build_id, self.platform)


class Build:
    def __init__(self, build_service, build_id: str, build_token: str):
        self.build_service = build_service
        self.build_id = build_id
        self.build_token = build_token
        self.buildkit = BuildKitService(build_token)

    def close(self):
        self.buildkit.close()
        self.build_service.finish_build(self.build_id)

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
        self.build_service = build_service
        self.build_id = build_id
        self.build_token = build_token
        self.buildkit = AsyncBuildKitService(build_token)

    async def close(self):
        await self.buildkit.close()
        await self.build_service.finish_build(self.build_id)

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
    def _create_channel_credentials(
        self, token: Optional[str] = None
    ) -> grpc.ChannelCredentials:
        channel_creds = grpc.ssl_channel_credentials()
        call_creds = grpc.access_token_call_credentials(
            token or os.getenv("DEPOT_API_TOKEN")
        )
        return grpc.composite_channel_credentials(channel_creds, call_creds)

    def _proto_to_datetime(self, timestamp: Timestamp) -> datetime:
        return datetime.fromtimestamp(timestamp.seconds + timestamp.nanos / 1e9)


class Client(BaseClient):
    def __init__(
        self,
        host: str = DEPOT_GRPC_HOST,
        port: int = DEPOT_GRPC_PORT,
        token: Optional[str] = None,
    ):
        credentials = self._create_channel_credentials(token)
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

    @contextmanager
    def create_endpoint(
        self, project_id: str, platform: Optional[str] = None
    ) -> Iterator[Endpoint]:
        with self.create_build(project_id) as build:
            with build.get_endpoint(platform=platform) as endpoint:
                yield endpoint


class AsyncClient(BaseClient):
    def __init__(
        self,
        host: str = DEPOT_GRPC_HOST,
        port: int = DEPOT_GRPC_PORT,
        token: Optional[str] = None,
    ):
        credentials = self._create_channel_credentials(token)
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

    @asynccontextmanager
    async def create_endpoint(
        self, project_id: str, platform: Optional[str] = None
    ) -> AsyncIterator[AsyncEndpoint]:
        async with self.create_build(project_id) as build:
            async with await build.get_endpoint(platform=platform) as endpoint:
                yield endpoint


def _main():
    with Client() as client:
        print(client.list_projects())
        project_id = "749dxclhrj"
        client.list_builds(project_id)
        with client.create_endpoint(project_id) as endpoint:
            print(repr(endpoint))
            assert isinstance(endpoint.cert, str)
            assert isinstance(endpoint.key, str)
            assert isinstance(endpoint.ca_cert, str)


async def _async_main():
    async with AsyncClient() as client:
        print(await client.list_projects())
        project_id = "749dxclhrj"
        await client.list_builds(project_id)
        async with await client.create_build(project_id) as build:
            async with await build.get_endpoint() as endpoint:
                print(repr(endpoint))
                assert isinstance(endpoint.cert, str)
                assert isinstance(endpoint.key, str)
                assert isinstance(endpoint.ca_cert, str)


if __name__ == "__main__":
    _main()
    asyncio.run(_async_main())
