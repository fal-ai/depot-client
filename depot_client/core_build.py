from dataclasses import dataclass

from depot_client.api.depot.core.v1.build_pb2 import (
    GetBuildRequest,
    ListBuildsRequest,
    ShareBuildRequest,
    StopSharingBuildRequest,
)
from depot_client.api.depot.core.v1.build_pb2_grpc import BuildServiceStub


@dataclass
class BuildInfo:
    build_id: str
    status: str


class CoreBuildService:
    def __init__(self, channel):
        self.stub = BuildServiceStub(channel)

    def share_build(self, build_id: str) -> str:
        request = ShareBuildRequest(build_id)
        return self.stub.ShareBuild(request).share_url

    def stop_sharing_build(self, build_id: str) -> None:
        request = StopSharingBuildRequest(build_id)
        self.stub.StopSharingBuild(request)

    def list_builds(self, project_id: str) -> list[BuildInfo]:
        # TODO: implement pagination with page_size/page_token
        request = ListBuildsRequest(project_id=project_id)
        response = self.stub.ListBuilds(request)
        return [BuildInfo(build.build_id, build.status) for build in response.builds]

    def get_build(self, build_id: str) -> BuildInfo:
        request = GetBuildRequest(build_id)
        response = self.stub.GetBuild(request)
        return BuildInfo(response.build.build_id, response.build.status)


class AsyncCoreBuildService:
    def __init__(self, channel):
        self.stub = BuildServiceStub(channel)

    async def share_build(self, build_id: str) -> str:
        request = ShareBuildRequest(build_id)
        response = await self.stub.ShareBuild(request)
        return response.share_url

    async def stop_sharing_build(self, build_id: str) -> None:
        request = StopSharingBuildRequest(build_id)
        await self.stub.StopSharingBuild(request)

    async def list_builds(self, project_id: str) -> list[BuildInfo]:
        # TODO: implement pagination with page_size/page_token
        request = ListBuildsRequest(project_id=project_id)
        response = await self.stub.ListBuilds(request)
        return [BuildInfo(build.build_id, build.status) for build in response.builds]

    async def get_build(self, build_id: str) -> BuildInfo:
        request = GetBuildRequest(build_id)
        response = await self.stub.GetBuild(request)
        return BuildInfo(response.build.build_id, response.build.status)
