from dataclasses import dataclass
from typing import List, Union

import grpc

import depot_client.api.depot.core.v1.project_pb2 as project_pb2
import depot_client.api.depot.core.v1.project_pb2_grpc as project_pb2_grpc


@dataclass
class ProjectInfo:
    project_id: str
    organization_id: str
    name: str
    region_id: str
    created_at: str
    hardware: str


@dataclass
class TokenInfo:
    token_id: str
    description: str


@dataclass
class TokenCreationInfo:
    token_id: str
    secret: str


@dataclass
class TrustPolicyInfo:
    trust_policy_id: str
    provider: Union[
        project_pb2.TrustPolicy.GitHub,
        project_pb2.TrustPolicy.CircleCI,
        project_pb2.TrustPolicy.Buildkite,
    ]


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
                created_at=project.created_at,
                hardware=project.hardware,
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
            created_at=response.project.created_at,
            hardware=response.project.hardware,
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
            created_at=response.project.created_at,
            hardware=response.project.hardware,
        )

    def delete_project(self, project_id: str) -> None:
        request = project_pb2.DeleteProjectRequest(project_id=project_id)
        self.stub.DeleteProject(request)

    def reset_project(self, project_id: str) -> None:
        request = project_pb2.ResetProjectRequest(project_id=project_id)
        self.stub.ResetProject(request)

    def list_trust_policies(self, project_id: str) -> List[TrustPolicyInfo]:
        request = project_pb2.ListTrustPoliciesRequest(project_id=project_id)
        response = self.stub.ListTrustPolicies(request)
        return [
            TrustPolicyInfo(
                trust_policy_id=policy.trust_policy_id,
                provider=policy.WhichOneof("provider"),
            )
            for policy in response.trust_policies
        ]

    def add_trust_policy(
        self,
        project_id: str,
        provider: Union[
            project_pb2.TrustPolicy.GitHub,
            project_pb2.TrustPolicy.CircleCI,
            project_pb2.TrustPolicy.Buildkite,
        ],
    ) -> TrustPolicyInfo:
        request = project_pb2.AddTrustPolicyRequest(project_id=project_id)

        if isinstance(provider, project_pb2.TrustPolicy.GitHub):
            request.github.CopyFrom(provider)
        elif isinstance(provider, project_pb2.TrustPolicy.CircleCI):
            request.circleci.CopyFrom(provider)
        elif isinstance(provider, project_pb2.TrustPolicy.Buildkite):
            request.buildkite.CopyFrom(provider)

        response = self.stub.AddTrustPolicy(request)
        return TrustPolicyInfo(
            trust_policy_id=response.trust_policy.trust_policy_id,
            provider=response.trust_policy.WhichOneof("provider"),
        )

    def remove_trust_policy(self, project_id: str, trust_policy_id: str) -> None:
        request = project_pb2.RemoveTrustPolicyRequest(
            project_id=project_id, trust_policy_id=trust_policy_id
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
        return [
            ProjectInfo(
                project_id=project.project_id,
                organization_id=project.organization_id,
                name=project.name,
                region_id=project.region_id,
                created_at=project.created_at,
                hardware=project.hardware,
            )
            for project in response.projects
        ]

    async def create_project(self, name: str, region_id: str) -> ProjectInfo:
        request = project_pb2.CreateProjectRequest(name=name, region_id=region_id)
        response = await self.stub.CreateProject(request)
        return ProjectInfo(
            project_id=response.project.project_id,
            organization_id=response.project.organization_id,
            name=response.project.name,
            region_id=response.project.region_id,
            created_at=response.project.created_at,
            hardware=response.project.hardware,
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
            created_at=response.project.created_at,
            hardware=response.project.hardware,
        )

    async def delete_project(self, project_id: str) -> None:
        request = project_pb2.DeleteProjectRequest(project_id=project_id)
        await self.stub.DeleteProject(request)

    async def reset_project(self, project_id: str) -> None:
        request = project_pb2.ResetProjectRequest(project_id=project_id)
        await self.stub.ResetProject(request)

    async def list_trust_policies(self, project_id: str) -> List[TrustPolicyInfo]:
        request = project_pb2.ListTrustPoliciesRequest(project_id=project_id)
        response = await self.stub.ListTrustPolicies(request)
        return [
            TrustPolicyInfo(
                trust_policy_id=policy.trust_policy_id,
                provider=policy.WhichOneof("provider"),
            )
            for policy in response.trust_policies
        ]

    async def add_trust_policy(
        self,
        project_id: str,
        provider: Union[
            project_pb2.TrustPolicy.GitHub,
            project_pb2.TrustPolicy.CircleCI,
            project_pb2.TrustPolicy.Buildkite,
        ],
    ) -> TrustPolicyInfo:
        request = project_pb2.AddTrustPolicyRequest(project_id=project_id)

        if isinstance(provider, project_pb2.TrustPolicy.GitHub):
            request.github.CopyFrom(provider)
        elif isinstance(provider, project_pb2.TrustPolicy.CircleCI):
            request.circleci.CopyFrom(provider)
        elif isinstance(provider, project_pb2.TrustPolicy.Buildkite):
            request.buildkite.CopyFrom(provider)

        response = await self.stub.AddTrustPolicy(request)
        return TrustPolicyInfo(
            trust_policy_id=response.trust_policy.trust_policy_id,
            provider=response.trust_policy.WhichOneof("provider"),
        )

    async def remove_trust_policy(self, project_id: str, trust_policy_id: str) -> None:
        request = project_pb2.RemoveTrustPolicyRequest(
            project_id=project_id, trust_policy_id=trust_policy_id
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
