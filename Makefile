protos:
	buf export buf.build/depot/api -o depot_client/protos

api:
	python -m grpc_tools.protoc \
	    --python_out=depot_client/api \
	    --grpc_python_out=depot_client/api \
	    --proto_path=depot_client/protos \
	    depot_client/protos/depot/build/v1/build.proto \
	    depot_client/protos/depot/buildkit/v1/buildkit.proto \
	    depot_client/protos/depot/core/v1/build.proto \
	    depot_client/protos/depot/core/v1/project.proto
	find depot_client/api -type f -name "*_pb2*.py" -exec sed -i '' 's/from depot\./from depot_client.api.depot./g' {} +

build:
	rm -rf dist
	python -m build

publish: build
	python -m twine upload dist/*
