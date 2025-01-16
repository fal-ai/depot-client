from dataclasses import dataclass
from typing import Optional

import grpc

from depot_client.api.depot.buildkit.v1.buildkit_pb2 import (
    GetEndpointRequest,
    Platform,
    ReleaseEndpointRequest,
    ReportHealthRequest,
)
from depot_client.api.depot.buildkit.v1.buildkit_pb2_grpc import BuildKitServiceStub

DEFAULT_PLATFORM = "amd64"

PLATFORM_MAP = {
    "amd64": "PLATFORM_AMD64",
    "arm64": "PLATFORM_ARM64",
}


def get_platform(platform: Optional[str] = None) -> str:
    return PLATFORM_MAP[platform or DEFAULT_PLATFORM]


@dataclass
class EndpointInfo:
    endpoint: str
    server_name: str
    cert: str
    key: str
    ca_cert: str


class BuildKitService:
    def __init__(self, token: str):
        creds = grpc.composite_channel_credentials(
            grpc.ssl_channel_credentials(),
            grpc.access_token_call_credentials(token),
        )
        self.channel = grpc.secure_channel("api.depot.dev:443", creds)
        self.stub = BuildKitServiceStub(self.channel)

    def close(self):
        self.channel.close()

    def get_endpoint(self, build_id: str, platform: Optional[str] = None):
        request = GetEndpointRequest(
            build_id=build_id,
            platform=Platform.Value(get_platform(platform)),
        )
        for response in self.stub.GetEndpoint(request):
            if response.HasField("pending"):
                continue
            elif response.HasField("active"):
                print(dir(response.active.cert))
                return EndpointInfo(
                    endpoint=response.active.endpoint,
                    server_name=response.active.server_name,
                    cert=response.active.cert.cert,
                    key=response.active.cert.key,
                    ca_cert=response.active.ca_cert,
                )
            else:
                raise ValueError("Unknown response type: {response}")

    def report_health(self, build_id: str, platform: Optional[str] = None) -> None:
        request = ReportHealthRequest(
            build_id=build_id,
            platform=Platform.Value(get_platform(platform)),
        )

        def request_generator():
            yield request

        self.stub.ReportHealth(request_generator())

    def release_endpoint(self, build_id: str, platform: Optional[str] = None) -> None:
        request = ReleaseEndpointRequest(
            build_id=build_id,
            platform=Platform.Value(get_platform(platform)),
        )
        self.stub.ReleaseEndpoint(request)


class AsyncBuildKitService:
    def __init__(self, token: str):
        creds = grpc.composite_channel_credentials(
            grpc.ssl_channel_credentials(),
            grpc.access_token_call_credentials(token),
        )
        self.channel = grpc.aio.secure_channel("api.depot.dev:443", creds)
        self.stub = BuildKitServiceStub(self.channel)

    async def close(self):
        await self.channel.close()

    async def get_endpoint(self, build_id: str, platform: Optional[str] = None):
        request = GetEndpointRequest(
            build_id=build_id,
            platform=Platform.Value(get_platform(platform)),
        )
        async for response in self.stub.GetEndpoint(request):
            if response.HasField("pending"):
                continue
            elif response.HasField("active"):
                print(dir(response.active.cert))
                return EndpointInfo(
                    endpoint=response.active.endpoint,
                    server_name=response.active.server_name,
                    cert=response.active.cert.cert,
                    key=response.active.cert.key,
                    ca_cert=response.active.ca_cert,
                )
            else:
                raise ValueError("Unknown response type: {response}")

    async def report_health(
        self, build_id: str, platform: Optional[str] = None
    ) -> None:
        request = ReportHealthRequest(
            build_id=build_id,
            platform=Platform.Value(get_platform(platform)),
        )

        def request_generator():
            yield request

        await self.stub.ReportHealth(request_generator())

    async def release_endpoint(
        self, build_id: str, platform: Optional[str] = None
    ) -> None:
        request = ReleaseEndpointRequest(
            build_id=build_id,
            platform=Platform.Value(get_platform(platform)),
        )
        await self.stub.ReleaseEndpoint(request)
