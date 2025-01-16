from typing import Optional, Tuple

import grpc

from depot_client.api.depot.build.v1.build_pb2 import (
    CreateBuildRequest,
    FinishBuildRequest,
)
from depot_client.api.depot.build.v1.build_pb2_grpc import BuildServiceStub


class BuildService:
    def __init__(self, channel: grpc.Channel):
        self.stub = BuildServiceStub(channel)

    def create_build(self, project_id: str) -> Tuple[str, str]:
        request = CreateBuildRequest(project_id=project_id)
        response = self.stub.CreateBuild(request)
        return response.build_id, response.build_token

    def finish_build(self, build_id: str, error: Optional[str] = None) -> None:
        if error is None:
            request = FinishBuildRequest(
                build_id=build_id,
                success=FinishBuildRequest.BuildSuccess(),
            )
        else:
            request = FinishBuildRequest(
                build_id=build_id,
                error=FinishBuildRequest.BuildError(error),
            )

        self.stub.FinishBuild(request)


class AsyncBuildService:
    def __init__(self, channel: grpc.Channel):
        self.stub = BuildServiceStub(channel)

    async def create_build(self, project_id: str) -> Tuple[str, str]:
        request = CreateBuildRequest(project_id=project_id)
        response = await self.stub.CreateBuild(request)
        return response.build_id, response.build_token

    async def finish_build(self, build_id: str, error: Optional[str] = None) -> None:
        if error is None:
            request = FinishBuildRequest(
                build_id=build_id,
                success=FinishBuildRequest.BuildSuccess(),
            )
        else:
            request = FinishBuildRequest(
                build_id=build_id,
                error=FinishBuildRequest.BuildError(error),
            )

        await self.stub.FinishBuild(request)
