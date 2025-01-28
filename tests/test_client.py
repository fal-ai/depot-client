from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import grpc
import pytest
from google.protobuf.timestamp_pb2 import Timestamp

from depot_client.api.depot.build.v1 import build_pb2
from depot_client.api.depot.buildkit.v1 import buildkit_pb2
from depot_client.api.depot.core.v1 import build_pb2 as core_build_pb2
from depot_client.client import AsyncClient, BuildEndpoint, Client


def create_timestamp(dt: datetime) -> Timestamp:
    ts = Timestamp()
    ts.FromDatetime(dt)
    return ts


class TestSyncClient:
    @pytest.fixture
    def client(self):
        with patch("grpc.secure_channel") as mock_channel:
            client = Client("test.depot.dev")
            mock_channel.assert_called_once_with(
                "test.depot.dev:443", grpc.ssl_channel_credentials()
            )
            yield client

    def test_create_build(self, client):
        expected_build_id = "build-123"
        expected_token = "token-456"

        client.build.CreateBuild.return_value = build_pb2.CreateBuildResponse(
            build_id=expected_build_id, build_token=expected_token
        )

        build_id, token = client.create_build("project-123")

        assert build_id == expected_build_id
        assert token == expected_token
        client.build.CreateBuild.assert_called_once_with(
            build_pb2.CreateBuildRequest(project_id="project-123")
        )

    def test_finish_build_success(self, client):
        client.finish_build("build-123")

        client.build.FinishBuild.assert_called_once()
        request = client.build.FinishBuild.call_args[0][0]
        assert request.build_id == "build-123"
        assert request.HasField("success")

    def test_finish_build_error(self, client):
        client.finish_build("build-123", error="Something went wrong")

        client.build.FinishBuild.assert_called_once()
        request = client.build.FinishBuild.call_args[0][0]
        assert request.build_id == "build-123"
        assert request.HasField("error")
        assert request.error.error == "Something went wrong"

    def test_get_endpoint(self, client):
        response = buildkit_pb2.GetEndpointResponse(
            active=buildkit_pb2.GetEndpointResponse.ActiveConnection(
                endpoint="tcp://1.2.3.4:1234",
                server_name="test-server",
                cert=buildkit_pb2.CertificatePair(
                    cert=buildkit_pb2.PublicCertificate(cert="client-cert"),
                    key=buildkit_pb2.PrivateKey(key="client-key"),
                ),
                ca_cert=buildkit_pb2.PublicCertificate(cert="ca-cert"),
            )
        )
        client.buildkit.GetEndpoint.return_value = [response]

        endpoints = list(client.get_endpoint("build-123"))
        assert len(endpoints) == 1
        endpoint = endpoints[0]
        assert isinstance(endpoint, BuildEndpoint)
        assert endpoint.endpoint == "tcp://1.2.3.4:1234"
        assert endpoint.server_name == "test-server"
        assert endpoint.client_cert == "client-cert"
        assert endpoint.client_key == "client-key"
        assert endpoint.ca_cert == "ca-cert"

    def test_get_build(self, client):
        now = datetime.now()
        response = core_build_pb2.GetBuildResponse(
            build=core_build_pb2.Build(
                build_id="build-123",
                status=core_build_pb2.Build.STATUS_SUCCESS,
                created_at=create_timestamp(now),
                build_duration_seconds=60,
            )
        )
        client.core_build.GetBuild.return_value = response

        build = client.get_build("build-123")

        assert build["build_id"] == "build-123"
        assert build["status"] == "STATUS_SUCCESS"
        assert build["created_at"].timestamp() == pytest.approx(now.timestamp())
        assert build["build_duration_seconds"] == 60


class TestAsyncClient:
    @pytest.fixture
    async def client(self):
        with patch("grpc.aio.secure_channel") as mock_channel:
            client = AsyncClient("test.depot.dev")
            mock_channel.assert_called_once()
            args = mock_channel.call_args[0]
            assert args[0] == "test.depot.dev:443"
            assert isinstance(args[1], grpc.ChannelCredentials)
            yield client
            await client.close()

    @pytest.mark.asyncio
    async def test_create_build(self, client):
        expected_build_id = "build-123"
        expected_token = "token-456"

        client.build.CreateBuild = AsyncMock(
            return_value=build_pb2.CreateBuildResponse(
                build_id=expected_build_id, build_token=expected_token
            )
        )

        build_id, token = await client.create_build("project-123")

        assert build_id == expected_build_id
        assert token == expected_token
        client.build.CreateBuild.assert_called_once_with(
            build_pb2.CreateBuildRequest(project_id="project-123")
        )

    @pytest.mark.asyncio
    async def test_finish_build_success(self, client):
        client.build.FinishBuild = AsyncMock()
        await client.finish_build("build-123")

        client.build.FinishBuild.assert_called_once()
        request = client.build.FinishBuild.call_args[0][0]
        assert request.build_id == "build-123"
        assert request.HasField("success")

    @pytest.mark.asyncio
    async def test_finish_build_error(self, client):
        client.build.FinishBuild = AsyncMock()
        await client.finish_build("build-123", error="Something went wrong")

        client.build.FinishBuild.assert_called_once()
        request = client.build.FinishBuild.call_args[0][0]
        assert request.build_id == "build-123"
        assert request.HasField("error")
        assert request.error.error == "Something went wrong"

    @pytest.mark.asyncio
    async def test_get_endpoint(self, client):
        response = buildkit_pb2.GetEndpointResponse(
            active=buildkit_pb2.GetEndpointResponse.ActiveConnection(
                endpoint="tcp://1.2.3.4:1234",
                server_name="test-server",
                cert=buildkit_pb2.CertificatePair(
                    cert=buildkit_pb2.PublicCertificate(cert="client-cert"),
                    key=buildkit_pb2.PrivateKey(key="client-key"),
                ),
                ca_cert=buildkit_pb2.PublicCertificate(cert="ca-cert"),
            )
        )

        # Mock async iterator
        async def mock_get_endpoint(_):
            yield response

        client.buildkit.GetEndpoint = Mock(return_value=mock_get_endpoint(None))

        endpoints = []
        async for endpoint in client.get_endpoint("build-123"):
            endpoints.append(endpoint)

        assert len(endpoints) == 1
        endpoint = endpoints[0]
        assert isinstance(endpoint, BuildEndpoint)
        assert endpoint.endpoint == "tcp://1.2.3.4:1234"
        assert endpoint.server_name == "test-server"
        assert endpoint.client_cert == "client-cert"
        assert endpoint.client_key == "client-key"
        assert endpoint.ca_cert == "ca-cert"

    @pytest.mark.asyncio
    async def test_get_build(self, client):
        now = datetime.now()
        response = core_build_pb2.GetBuildResponse(
            build=core_build_pb2.Build(
                build_id="build-123",
                status=core_build_pb2.Build.STATUS_SUCCESS,
                created_at=create_timestamp(now),
                build_duration_seconds=60,
            )
        )
        client.core_build.GetBuild = AsyncMock(return_value=response)

        build = await client.get_build("build-123")

        assert build["build_id"] == "build-123"
        assert build["status"] == "STATUS_SUCCESS"
        assert build["created_at"].timestamp() == pytest.approx(now.timestamp())
        assert build["build_duration_seconds"] == 60
