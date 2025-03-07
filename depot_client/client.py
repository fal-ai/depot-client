import asyncio
import json
import logging
import os
import threading
import time
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass
from datetime import datetime
from typing import AsyncIterator, Iterator, List, Optional, Union

import grpc
import grpc.aio
from google.protobuf.timestamp_pb2 import Timestamp

from depot_client.build import AsyncBuildService, BuildService
from depot_client.buildkit import AsyncBuildKitService, BuildKitService, EndpointInfo
from depot_client.core_build import AsyncCoreBuildService, BuildInfo, CoreBuildService
from depot_client.project import (
    AsyncProjectService,
    ProjectInfo,
    ProjectService,
    TokenCreationInfo,
    TokenInfo,
    TrustPolicy,
)

DEPOT_GRPC_HOST = "api.depot.dev"
DEPOT_GRPC_PORT = 443

SERVICE_CONFIG_JSON = json.dumps(
    {
        "methodConfig": [
            {
                "name": [{}],
                "retryPolicy": {
                    "maxAttempts": 5,
                    "initialBackoff": "0.1s",
                    "maxBackoff": "5s",
                    "backoffMultiplier": 2,
                    "retryableStatusCodes": ["UNAVAILABLE"],
                },
            }
        ]
    }
)

CHANNEL_OPTIONS = [
    ("grpc.enable_retries", 1),
    ("grpc.service_config", SERVICE_CONFIG_JSON),
]

REPORT_HEALTH_INTERVAL = 30
REPORT_HEALTH_SLEEP_INTERVAL = 0.1
REPORT_HEALTH_CANCEL_TIMEOUT = 1

logger = logging.getLogger(__name__)


@dataclass
class Endpoint:
    build_id: str
    platform: str
    buildkit: BuildKitService
    _info: Optional[EndpointInfo] = None

    @property
    def endpoint(self) -> str:
        return self._info.endpoint

    @property
    def server_name(self) -> str:
        return self._info.server_name

    @property
    def cert(self) -> str:
        return self._info.cert

    @property
    def key(self) -> str:
        return self._info.key

    @property
    def ca_cert(self) -> str:
        return self._info.ca_cert

    def _health_callback(self):
        start = time.time()
        while time.time() - start < REPORT_HEALTH_INTERVAL:
            if self._stop_health.is_set():
                return False
            time.sleep(REPORT_HEALTH_SLEEP_INTERVAL)
        return True

    def __enter__(self):
        self._stop_health = threading.Event()
        self._health_thread = threading.Thread(
            target=self.buildkit.report_health,
            args=(self.build_id, self.platform, self._health_callback),
            daemon=True,
        )
        self._health_thread.start()
        self._info = self.buildkit.get_endpoint(self.build_id, self.platform)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._stop_health.set()
        self._health_thread.join(timeout=REPORT_HEALTH_CANCEL_TIMEOUT)
        self.close()
        self._info = None

    def close(self):
        self.buildkit.release_endpoint(self.build_id, self.platform)


@dataclass
class AsyncEndpoint:
    build_id: str
    platform: str
    buildkit: AsyncBuildKitService
    _info: Optional[EndpointInfo] = None

    @property
    def endpoint(self) -> str:
        return self._info.endpoint

    @property
    def server_name(self) -> str:
        return self._info.server_name

    @property
    def cert(self) -> str:
        return self._info.cert

    @property
    def key(self) -> str:
        return self._info.key

    @property
    def ca_cert(self) -> str:
        return self._info.ca_cert

    async def _health_callback(self):
        await asyncio.sleep(REPORT_HEALTH_INTERVAL)
        return True

    async def __aenter__(self):
        self._health_task = asyncio.create_task(self._health_callback())
        self._info = await self.buildkit.get_endpoint(self.build_id, self.platform)
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        self._health_task.cancel()
        try:
            await asyncio.wait_for(
                self._health_task, timeout=REPORT_HEALTH_CANCEL_TIMEOUT
            )
        except (asyncio.CancelledError, asyncio.TimeoutError):
            pass
        await self.close()
        self._info = None

    async def close(self):
        await self.buildkit.release_endpoint(self.build_id, self.platform)


class Build:
    def __init__(
        self,
        build_service,
        build_id: str,
        build_token: str,
        buildkit_host: str = DEPOT_GRPC_HOST,
        buildkit_port: int = DEPOT_GRPC_PORT,
    ):
        self.build_service = build_service
        self.build_id = build_id
        self.build_token = build_token
        self.buildkit = BuildKitService(
            buildkit_host,
            buildkit_port,
            build_token,
        )

    def close(self):
        self.buildkit.close()
        self.build_service.finish_build(self.build_id)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def get_endpoint(self, platform: Optional[str] = None) -> Endpoint:
        return Endpoint(
            build_id=self.build_id,
            platform=platform,
            buildkit=self.buildkit,
        )


class AsyncBuild:
    def __init__(
        self,
        build_service,
        build_id: str,
        build_token: str,
        buildkit_host: str = DEPOT_GRPC_HOST,
        buildkit_port: int = DEPOT_GRPC_PORT,
    ):
        self.build_service = build_service
        self.build_id = build_id
        self.build_token = build_token
        self.buildkit = AsyncBuildKitService(
            buildkit_host,
            buildkit_port,
            build_token,
        )

    async def close(self):
        await self.buildkit.close()
        await self.build_service.finish_build(self.build_id)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()

    async def get_endpoint(self, platform: Optional[str] = None) -> AsyncEndpoint:
        return AsyncEndpoint(
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
        self.host = host
        self.port = port
        self.channel = grpc.secure_channel(
            f"{host}:{port}",
            credentials,
            options=CHANNEL_OPTIONS,
        )
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

    def get_project(self, project_id: str) -> ProjectInfo:
        return self.project.get_project(project_id)

    def create_project(
        self,
        name: str,
        organization_id: Optional[str] = None,
        region_id: Optional[str] = None,
        cache_policy: Optional[dict] = None,
        hardware: Optional[str] = None,
    ) -> ProjectInfo:
        return self.project.create_project(
            name=name,
            organization_id=organization_id,
            region_id=region_id,
            cache_policy=cache_policy,
            hardware=hardware,
        )

    def update_project(
        self,
        project_id: str,
        name: Optional[str] = None,
        region_id: Optional[str] = None,
        cache_policy: Optional[dict] = None,
        hardware: Optional[str] = None,
    ) -> ProjectInfo:
        return self.project.update_project(
            project_id=project_id,
            name=name,
            region_id=region_id,
            cache_policy=cache_policy,
            hardware=hardware,
        )

    def delete_project(self, project_id: str) -> None:
        return self.project.delete_project(project_id)

    def reset_project(self, project_id: str) -> None:
        return self.project.reset_project(project_id)

    def list_trust_policies(self, project_id: str) -> List[TrustPolicy]:
        return self.project.list_trust_policies(project_id)

    def add_trust_policy(
        self,
        project_id: str,
        provider: Union[dict, None] = None,
        buildkite: Optional[dict] = None,
        circleci: Optional[dict] = None,
        github: Optional[dict] = None,
    ) -> TrustPolicy:
        return self.project.add_trust_policy(
            project_id=project_id,
            provider=provider,
            buildkite=buildkite,
            circleci=circleci,
            github=github,
        )

    def remove_trust_policy(self, project_id: str, trust_policy_id: str) -> None:
        return self.project.remove_trust_policy(project_id, trust_policy_id)

    def list_tokens(self, project_id: str) -> List[TokenInfo]:
        return self.project.list_tokens(project_id)

    def create_token(self, project_id: str, description: str) -> TokenCreationInfo:
        return self.project.create_token(project_id, description)

    def update_token(self, token_id: str, description: str) -> None:
        return self.project.update_token(token_id, description)

    def delete_token(self, token_id: str) -> None:
        return self.project.delete_token(token_id)


class AsyncClient(BaseClient):
    def __init__(
        self,
        host: str = DEPOT_GRPC_HOST,
        port: int = DEPOT_GRPC_PORT,
        token: Optional[str] = None,
    ):
        credentials = self._create_channel_credentials(token)
        self.channel = grpc.aio.secure_channel(
            f"{host}:{port}",
            credentials,
            options=CHANNEL_OPTIONS,
        )
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
        async with await self.create_build(project_id) as build:
            async with await build.get_endpoint(platform=platform) as endpoint:
                yield endpoint

    async def get_project(self, project_id: str) -> ProjectInfo:
        return await self.project.get_project(project_id)

    async def create_project(
        self,
        name: str,
        organization_id: Optional[str] = None,
        region_id: Optional[str] = None,
        cache_policy: Optional[dict] = None,
        hardware: Optional[str] = None,
    ) -> ProjectInfo:
        return await self.project.create_project(
            name=name,
            organization_id=organization_id,
            region_id=region_id,
            cache_policy=cache_policy,
            hardware=hardware,
        )

    async def update_project(
        self,
        project_id: str,
        name: Optional[str] = None,
        region_id: Optional[str] = None,
        cache_policy: Optional[dict] = None,
        hardware: Optional[str] = None,
    ) -> ProjectInfo:
        return await self.project.update_project(
            project_id=project_id,
            name=name,
            region_id=region_id,
            cache_policy=cache_policy,
            hardware=hardware,
        )

    async def delete_project(self, project_id: str) -> None:
        return await self.project.delete_project(project_id)

    async def reset_project(self, project_id: str) -> None:
        return await self.project.reset_project(project_id)

    async def list_trust_policies(self, project_id: str) -> List[TrustPolicy]:
        return await self.project.list_trust_policies(project_id)

    async def add_trust_policy(
        self,
        project_id: str,
        provider: Union[dict, None] = None,
        buildkite: Optional[dict] = None,
        circleci: Optional[dict] = None,
        github: Optional[dict] = None,
    ) -> TrustPolicy:
        return await self.project.add_trust_policy(
            project_id=project_id,
            provider=provider,
            buildkite=buildkite,
            circleci=circleci,
            github=github,
        )

    async def remove_trust_policy(self, project_id: str, trust_policy_id: str) -> None:
        return await self.project.remove_trust_policy(project_id, trust_policy_id)

    async def list_tokens(self, project_id: str) -> List[TokenInfo]:
        return await self.project.list_tokens(project_id)

    async def create_token(
        self, project_id: str, description: str
    ) -> TokenCreationInfo:
        return await self.project.create_token(project_id, description)

    async def update_token(self, token_id: str, description: str) -> None:
        return await self.project.update_token(token_id, description)

    async def delete_token(self, token_id: str) -> None:
        return await self.project.delete_token(token_id)


def _main():
    with Client() as client:
        print(client.list_projects())
        project_id = "749dxclhrj"
        client.list_builds(project_id)
        with client.create_endpoint(project_id) as endpoint:
            print(repr(endpoint))
            time.sleep(90)
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
                await asyncio.sleep(90)
                assert isinstance(endpoint.cert, str)
                assert isinstance(endpoint.key, str)
                assert isinstance(endpoint.ca_cert, str)


if __name__ == "__main__":
    _main()
    asyncio.run(_async_main())
