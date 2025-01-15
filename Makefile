protos:
	buf export buf.build/depot/api -o depotdev/protos

api:
	rm -rf depotdev/api/*
	python -m grpc_tools.protoc \
	    --python_out=depotdev/api \
	    --grpc_python_out=depotdev/api \
	    --proto_path=depotdev/protos \
	    depotdev/protos/depot/build/v1/build.proto \
	    depotdev/protos/depot/buildkit/v1/buildkit.proto \
	    depotdev/protos/depot/core/v1/build.proto \
	    depotdev/protos/depot/core/v1/project.proto
	find depotdev/api -type f -name "*_pb2*.py" -exec sed -i '' 's/from depot\./from depotdev.api.depot./g' {} +
