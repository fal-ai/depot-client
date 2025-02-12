from dataclasses import dataclass
from typing import List, Optional, Union

import grpc

import depot_client.api.depot.core.v1.project_pb2 as project_pb2
import depot_client.api.depot.core.v1.project_pb2_grpc as project_pb2_grpc
from depot_client.api.depot.core.v1.project_pb2 import (
    Project as ProjectProto,
)
from depot_client.api.depot.core.v1.project_pb2 import (
    TrustPolicy as TrustPolicyProto,
)


@dataclass
class ProjectInfo:
    project_id: str
    organization_id: str
    name: str
    region_id: str
    created_at: str
    cache_policy: Optional[dict] = None
    hardware: Optional[str] = None

    @classmethod
    def from_proto(cls, proto: ProjectProto) -> "ProjectInfo":
        return cls(
            project_id=proto.project_id,
            organization_id=proto.organization_id,
            name=proto.name,
            region_id=proto.region_id,
            created_at=proto.created_at.ToDatetime().isoformat(),
            cache_policy=proto.cache_policy if proto.HasField("cache_policy") else None,
            hardware=proto.hardware if proto.hardware != 0 else None,
        )


@dataclass
class TokenInfo:
    token_id: str
    description: str


@dataclass
class TokenCreationInfo:
    token_id: str
    secret: str


@dataclass
class TrustPolicyGitHub:
    repository_owner: str
    repository: str


@dataclass
class TrustPolicyCircleCI:
    organization_uuid: str
    project_uuid: str


@dataclass
class TrustPolicyBuildkite:
    organization_slug: str
    pipeline_slug: str


@dataclass
class TrustPolicy:
    trust_policy_id: str
    github: Optional[TrustPolicyGitHub] = None
    circleci: Optional[TrustPolicyCircleCI] = None
    buildkite: Optional[TrustPolicyBuildkite] = None

    @classmethod
    def from_proto(cls, proto: TrustPolicyProto) -> "TrustPolicy":
        kwargs = {"trust_policy_id": proto.trust_policy_id}

        if proto.HasField("github"):
            kwargs["github"] = TrustPolicyGitHub(
                repository_owner=proto.github.repository_owner,
                repository=proto.github.repository,
            )
        elif proto.HasField("circleci"):
            kwargs["circleci"] = TrustPolicyCircleCI(
                organization_uuid=proto.circleci.organization_uuid,
                project_uuid=proto.circleci.project_uuid,
            )
        elif proto.HasField("buildkite"):
            kwargs["buildkite"] = TrustPolicyBuildkite(
                organization_slug=proto.buildkite.organization_slug,
                pipeline_slug=proto.buildkite.pipeline_slug,
            )

        return cls(**kwargs)


class ProjectService:
    def __init__(self, channel: grpc.Channel):
        self.stub = project_pb2_grpc.ProjectServiceStub(channel)

    def list_projects(self) -> List[ProjectInfo]:
        request = project_pb2.ListProjectsRequest()
        response = self.stub.ListProjects(request)
        return [ProjectInfo.from_proto(project) for project in response.projects]

    def create_project(self, name: str, region_id: str) -> ProjectInfo:
        request = project_pb2.CreateProjectRequest(name=name, region_id=region_id)
        response = self.stub.CreateProject(request)
        return ProjectInfo.from_proto(response.project)

    def update_project(self, project_id: str, name: str, region_id: str) -> ProjectInfo:
        request = project_pb2.UpdateProjectRequest(
            project_id=project_id, name=name, region_id=region_id
        )
        response = self.stub.UpdateProject(request)
        return ProjectInfo.from_proto(response.project)

    def delete_project(self, project_id: str) -> None:
        request = project_pb2.DeleteProjectRequest(project_id=project_id)
        self.stub.DeleteProject(request)

    def reset_project(self, project_id: str) -> None:
        request = project_pb2.ResetProjectRequest(project_id=project_id)
        self.stub.ResetProject(request)

    def list_trust_policies(self, project_id: str) -> List[TrustPolicy]:
        request = project_pb2.ListTrustPoliciesRequest(project_id=project_id)
        response = self.stub.ListTrustPolicies(request)
        return [TrustPolicy.from_proto(policy) for policy in response.trust_policies]

    def add_trust_policy(
        self,
        project_id: str,
        provider: Union[dict, None] = None,
        buildkite: Optional[dict] = None,
        circleci: Optional[dict] = None,
        github: Optional[dict] = None,
    ) -> TrustPolicy:
        if provider:
            # Handle legacy provider dict
            if provider.get("type") == "github":
                github = provider
            elif provider.get("type") == "circleci":
                circleci = provider
            elif provider.get("type") == "buildkite":
                buildkite = provider

        request = project_pb2.AddTrustPolicyRequest(project_id=project_id)

        if github:
            request.github.repository_owner = github["repository_owner"]
            request.github.repository = github["repository"]
        elif circleci:
            request.circleci.organization_uuid = circleci["organization_uuid"]
            request.circleci.project_uuid = circleci["project_uuid"]
        elif buildkite:
            request.buildkite.organization_slug = buildkite["organization_slug"]
            request.buildkite.pipeline_slug = buildkite["pipeline_slug"]

        response = self.stub.AddTrustPolicy(request)
        return TrustPolicy.from_proto(response.trust_policy)

    def remove_trust_policy(self, project_id: str, trust_policy_id: str) -> None:
        request = project_pb2.RemoveTrustPolicyRequest(
            project_id=project_id,
            trust_policy_id=trust_policy_id,
        )
        self.stub.RemoveTrustPolicy(request)

    def list_tokens(self, project_id: str) -> List[TokenInfo]:
        request = project_pb2.ListTokensRequest(project_id=project_id)
        response = self.stub.ListTokens(request)
        return [
            TokenInfo(token_id=token.token_id, description=token.description)
            for token in response.tokens
        ]

    def create_token(self, project_id: str, description: str) -> TokenCreationInfo:
        request = project_pb2.CreateTokenRequest(
            project_id=project_id, description=description
        )
        response = self.stub.CreateToken(request)
        return TokenCreationInfo(token_id=response.token_id, secret=response.secret)

    def update_token(self, token_id: str, description: str) -> None:
        request = project_pb2.UpdateTokenRequest(
            token_id=token_id, description=description
        )
        self.stub.UpdateToken(request)

    def delete_token(self, token_id: str) -> None:
        request = project_pb2.DeleteTokenRequest(token_id=token_id)
        self.stub.DeleteToken(request)


class AsyncProjectService:
    def __init__(self, channel: grpc.Channel):
        self.stub = project_pb2_grpc.ProjectServiceStub(channel)

    async def list_projects(self) -> List[ProjectInfo]:
        request = project_pb2.ListProjectsRequest()
        response = await self.stub.ListProjects(request)
        return [ProjectInfo.from_proto(project) for project in response.projects]

    async def create_project(self, name: str, region_id: str) -> ProjectInfo:
        request = project_pb2.CreateProjectRequest(name=name, region_id=region_id)
        response = await self.stub.CreateProject(request)
        return ProjectInfo.from_proto(response.project)

    async def update_project(
        self, project_id: str, name: str, region_id: str
    ) -> ProjectInfo:
        request = project_pb2.UpdateProjectRequest(
            project_id=project_id, name=name, region_id=region_id
        )
        response = await self.stub.UpdateProject(request)
        return ProjectInfo.from_proto(response.project)

    async def delete_project(self, project_id: str) -> None:
        request = project_pb2.DeleteProjectRequest(project_id=project_id)
        await self.stub.DeleteProject(request)

    async def reset_project(self, project_id: str) -> None:
        request = project_pb2.ResetProjectRequest(project_id=project_id)
        await self.stub.ResetProject(request)

    async def list_trust_policies(self, project_id: str) -> List[TrustPolicy]:
        request = project_pb2.ListTrustPoliciesRequest(project_id=project_id)
        response = await self.stub.ListTrustPolicies(request)
        return [TrustPolicy.from_proto(policy) for policy in response.trust_policies]

    async def add_trust_policy(
        self,
        project_id: str,
        provider: Union[dict, None] = None,
        buildkite: Optional[dict] = None,
        circleci: Optional[dict] = None,
        github: Optional[dict] = None,
    ) -> TrustPolicy:
        if provider:
            # Handle legacy provider dict
            if provider.get("type") == "github":
                github = provider
            elif provider.get("type") == "circleci":
                circleci = provider
            elif provider.get("type") == "buildkite":
                buildkite = provider

        request = project_pb2.AddTrustPolicyRequest(project_id=project_id)

        if github:
            request.github.repository_owner = github["repository_owner"]
            request.github.repository = github["repository"]
        elif circleci:
            request.circleci.organization_uuid = circleci["organization_uuid"]
            request.circleci.project_uuid = circleci["project_uuid"]
        elif buildkite:
            request.buildkite.organization_slug = buildkite["organization_slug"]
            request.buildkite.pipeline_slug = buildkite["pipeline_slug"]

        response = await self.stub.AddTrustPolicy(request)
        return TrustPolicy.from_proto(response.trust_policy)

    async def remove_trust_policy(self, project_id: str, trust_policy_id: str) -> None:
        request = project_pb2.RemoveTrustPolicyRequest(
            project_id=project_id,
            trust_policy_id=trust_policy_id,
        )
        await self.stub.RemoveTrustPolicy(request)

    async def list_tokens(self, project_id: str) -> List[TokenInfo]:
        request = project_pb2.ListTokensRequest(project_id=project_id)
        response = await self.stub.ListTokens(request)
        return [
            TokenInfo(token_id=token.token_id, description=token.description)
            for token in response.tokens
        ]

    async def create_token(
        self, project_id: str, description: str
    ) -> TokenCreationInfo:
        request = project_pb2.CreateTokenRequest(
            project_id=project_id, description=description
        )
        response = await self.stub.CreateToken(request)
        return TokenCreationInfo(token_id=response.token_id, secret=response.secret)

    async def update_token(self, token_id: str, description: str) -> None:
        request = project_pb2.UpdateTokenRequest(
            token_id=token_id, description=description
        )
        await self.stub.UpdateToken(request)

    async def delete_token(self, token_id: str) -> None:
        request = project_pb2.DeleteTokenRequest(token_id=token_id)
        await self.stub.DeleteToken(request)
