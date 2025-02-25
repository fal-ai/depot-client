# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from depot_client.api.depot.core.v1 import build_pb2 as depot_dot_core_dot_v1_dot_build__pb2

GRPC_GENERATED_VERSION = '1.64.0'
GRPC_VERSION = grpc.__version__
EXPECTED_ERROR_RELEASE = '1.65.0'
SCHEDULED_RELEASE_DATE = 'June 25, 2024'
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    warnings.warn(
        f'The grpc package installed is at version {GRPC_VERSION},'
        + f' but the generated code in depot/core/v1/build_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
        + f' This warning will become an error in {EXPECTED_ERROR_RELEASE},'
        + f' scheduled for release on {SCHEDULED_RELEASE_DATE}.',
        RuntimeWarning
    )


class BuildServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.ShareBuild = channel.unary_unary(
                '/depot.core.v1.BuildService/ShareBuild',
                request_serializer=depot_dot_core_dot_v1_dot_build__pb2.ShareBuildRequest.SerializeToString,
                response_deserializer=depot_dot_core_dot_v1_dot_build__pb2.ShareBuildResponse.FromString,
                _registered_method=True)
        self.StopSharingBuild = channel.unary_unary(
                '/depot.core.v1.BuildService/StopSharingBuild',
                request_serializer=depot_dot_core_dot_v1_dot_build__pb2.StopSharingBuildRequest.SerializeToString,
                response_deserializer=depot_dot_core_dot_v1_dot_build__pb2.StopSharingBuildResponse.FromString,
                _registered_method=True)
        self.ListBuilds = channel.unary_unary(
                '/depot.core.v1.BuildService/ListBuilds',
                request_serializer=depot_dot_core_dot_v1_dot_build__pb2.ListBuildsRequest.SerializeToString,
                response_deserializer=depot_dot_core_dot_v1_dot_build__pb2.ListBuildsResponse.FromString,
                _registered_method=True)
        self.GetBuild = channel.unary_unary(
                '/depot.core.v1.BuildService/GetBuild',
                request_serializer=depot_dot_core_dot_v1_dot_build__pb2.GetBuildRequest.SerializeToString,
                response_deserializer=depot_dot_core_dot_v1_dot_build__pb2.GetBuildResponse.FromString,
                _registered_method=True)


class BuildServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def ShareBuild(self, request, context):
        """Share a URL to a build with users outside of your organization
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def StopSharingBuild(self, request, context):
        """Stop sharing a build
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ListBuilds(self, request, context):
        """List the builds in your organization
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetBuild(self, request, context):
        """Get the build metadata of a build
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_BuildServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'ShareBuild': grpc.unary_unary_rpc_method_handler(
                    servicer.ShareBuild,
                    request_deserializer=depot_dot_core_dot_v1_dot_build__pb2.ShareBuildRequest.FromString,
                    response_serializer=depot_dot_core_dot_v1_dot_build__pb2.ShareBuildResponse.SerializeToString,
            ),
            'StopSharingBuild': grpc.unary_unary_rpc_method_handler(
                    servicer.StopSharingBuild,
                    request_deserializer=depot_dot_core_dot_v1_dot_build__pb2.StopSharingBuildRequest.FromString,
                    response_serializer=depot_dot_core_dot_v1_dot_build__pb2.StopSharingBuildResponse.SerializeToString,
            ),
            'ListBuilds': grpc.unary_unary_rpc_method_handler(
                    servicer.ListBuilds,
                    request_deserializer=depot_dot_core_dot_v1_dot_build__pb2.ListBuildsRequest.FromString,
                    response_serializer=depot_dot_core_dot_v1_dot_build__pb2.ListBuildsResponse.SerializeToString,
            ),
            'GetBuild': grpc.unary_unary_rpc_method_handler(
                    servicer.GetBuild,
                    request_deserializer=depot_dot_core_dot_v1_dot_build__pb2.GetBuildRequest.FromString,
                    response_serializer=depot_dot_core_dot_v1_dot_build__pb2.GetBuildResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'depot.core.v1.BuildService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('depot.core.v1.BuildService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class BuildService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def ShareBuild(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/depot.core.v1.BuildService/ShareBuild',
            depot_dot_core_dot_v1_dot_build__pb2.ShareBuildRequest.SerializeToString,
            depot_dot_core_dot_v1_dot_build__pb2.ShareBuildResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def StopSharingBuild(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/depot.core.v1.BuildService/StopSharingBuild',
            depot_dot_core_dot_v1_dot_build__pb2.StopSharingBuildRequest.SerializeToString,
            depot_dot_core_dot_v1_dot_build__pb2.StopSharingBuildResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def ListBuilds(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/depot.core.v1.BuildService/ListBuilds',
            depot_dot_core_dot_v1_dot_build__pb2.ListBuildsRequest.SerializeToString,
            depot_dot_core_dot_v1_dot_build__pb2.ListBuildsResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def GetBuild(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/depot.core.v1.BuildService/GetBuild',
            depot_dot_core_dot_v1_dot_build__pb2.GetBuildRequest.SerializeToString,
            depot_dot_core_dot_v1_dot_build__pb2.GetBuildResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
