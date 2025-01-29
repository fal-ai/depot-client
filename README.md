# depot-client

A Python client library for interacting with the [Depot](depot.dev) API, supporting both synchronous and asynchronous operations.

## Installation

```bash
pip install depot-client
```

## Usage

### Buildkit

#### Synchronous Client

```python
from depot_client import Client

with Client(token=DEPOT_API_TOKEN) as client:
    with client.create_endpoint(project_id=PROJECT_ID, platform="amd64") as endpoint:
        # Write certificates to files
        with open("client.crt", "w") as f:
            f.write(endpoint.cert)
        with open("client.key", "w") as f:
            f.write(endpoint.key)
        with open("ca.crt", "w") as f:
            f.write(endpoint.ca_cert)

        # Use with buildctl
        # buildctl --addr endpoint.endpoint \
        #     --tlscacert ca.crt \
        #     --tlscert client.crt \
        #     --tlskey client.key \
        #     build --frontend dockerfile.v0
```

#### Asynchronous Client

```python
import aiofiles
from depot_client import AsyncClient

async def main():
    async with AsyncClient(token=DEPOT_API_TOKEN) as client:
        async with await client.create_endpoint(project_id=PROJECT_ID) as endpoint:
            # Write certificates to files
            async with aiofiles.open("client.crt", "w") as f:
                await f.write(endpoint.cert)
            async with aiofiles.open("client.key", "w") as f:
                await f.write(endpoint.key)
            async with aiofiles.open("ca.crt", "w") as f:
                await f.write(endpoint.ca_cert)

            # Use with buildctl
            # buildctl --addr endpoint.endpoint \
            #     --tlscacert ca.crt \
            #     --tlscert client.crt \
            #     --tlskey client.key \
            #     build --frontend dockerfile.v0

asyncio.run(main())
```

## Features

- Synchronous and asynchronous APIs
- Easy BuildKit endpoint creation
- [Python bindings](https://github.com/fal-ai/depot-client/tree/main/depot_client/api) for [depot's gRPC](https://buf.build/depot/api) as well as [friendly pythonic wrappers](https://github.com/fal-ai/depot-client/blob/main/depot_client/project.py)

## API Reference

### Client Methods

- `create_endpoint(project_id, platform=None)`: Create a BuildKit endpoint
- `list_projects()`: Get available projects
- `create_build(project_id)`: Create a new build
- `finish_build(build_id, error=None)`: Complete a build
- `share_build(build_id)`: Share a build
- `stop_sharing_build(build_id)`: Stop sharing a build
- `get_build(build_id)`: Get build information
- `list_builds(project_id)`: List project builds

### Environment Variables

- `DEPOT_API_TOKEN`: Your Depot API token for authentication
