# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: depot/build/v1/build.proto
# Protobuf Python Version: 5.26.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1a\x64\x65pot/build/v1/build.proto\x12\x0e\x64\x65pot.build.v1\"(\n\x12\x43reateBuildRequest\x12\x12\n\nproject_id\x18\x01 \x01(\t\"<\n\x13\x43reateBuildResponse\x12\x10\n\x08\x62uild_id\x18\x01 \x01(\t\x12\x13\n\x0b\x62uild_token\x18\x02 \x01(\t\"\xe1\x01\n\x12\x46inishBuildRequest\x12\x10\n\x08\x62uild_id\x18\x01 \x01(\t\x12\x42\n\x07success\x18\x02 \x01(\x0b\x32/.depot.build.v1.FinishBuildRequest.BuildSuccessH\x00\x12>\n\x05\x65rror\x18\x03 \x01(\x0b\x32-.depot.build.v1.FinishBuildRequest.BuildErrorH\x00\x1a\x0e\n\x0c\x42uildSuccess\x1a\x1b\n\nBuildError\x12\r\n\x05\x65rror\x18\x01 \x01(\tB\x08\n\x06result\"\x15\n\x13\x46inishBuildResponse2\xbe\x01\n\x0c\x42uildService\x12V\n\x0b\x43reateBuild\x12\".depot.build.v1.CreateBuildRequest\x1a#.depot.build.v1.CreateBuildResponse\x12V\n\x0b\x46inishBuild\x12\".depot.build.v1.FinishBuildRequest\x1a#.depot.build.v1.FinishBuildResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'depot.build.v1.build_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_CREATEBUILDREQUEST']._serialized_start=46
  _globals['_CREATEBUILDREQUEST']._serialized_end=86
  _globals['_CREATEBUILDRESPONSE']._serialized_start=88
  _globals['_CREATEBUILDRESPONSE']._serialized_end=148
  _globals['_FINISHBUILDREQUEST']._serialized_start=151
  _globals['_FINISHBUILDREQUEST']._serialized_end=376
  _globals['_FINISHBUILDREQUEST_BUILDSUCCESS']._serialized_start=323
  _globals['_FINISHBUILDREQUEST_BUILDSUCCESS']._serialized_end=337
  _globals['_FINISHBUILDREQUEST_BUILDERROR']._serialized_start=339
  _globals['_FINISHBUILDREQUEST_BUILDERROR']._serialized_end=366
  _globals['_FINISHBUILDRESPONSE']._serialized_start=378
  _globals['_FINISHBUILDRESPONSE']._serialized_end=399
  _globals['_BUILDSERVICE']._serialized_start=402
  _globals['_BUILDSERVICE']._serialized_end=592
# @@protoc_insertion_point(module_scope)
