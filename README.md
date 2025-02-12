# depot-client

A Python client library for interacting with the [Depot](https://depot.dev) API, supporting both synchronous and asynchronous operations.

## Installation

```bash
pip install depot-client
```

## Usage

### Project Management

```python
from depot_client import Client

with Client(token=DEPOT_API_TOKEN) as client:
    # List all projects
    projects = client.list_projects()
    
    # Create a new project
    project = client.create_project(
        name="my-project",
        region_id="us-east-1"
    )
    
    # Update project
    updated = client.update_project(
        project_id=project.project_id,
        name="new-name",
        region_id="us-west-1"
    )
    
    # Manage project tokens
    tokens = client.list_tokens(project.project_id)
    new_token = client.create_token(
        project_id=project.project_id,
        description="CI/CD token"
    )
    
    # Trust policies
    policies = client.list_trust_policies(project.project_id)
    github_policy = client.add_trust_policy(
        project_id=project.project_id,
        github={
            "repository_owner": "org",
            "repository": "repo"
        }
    )
```

### BuildKit Integration

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
        #     --tlsservername endpoint.server_name \
        #     --tlscacert ca.crt \
        #     --tlscert client.crt \
        #     --tlskey client.key \
        #     build --frontend dockerfile.v0
```

#### Asynchronous Client

```python
import asyncio
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

asyncio.run(main())
```

### Build Management

```python
with Client(token=DEPOT_API_TOKEN) as client:
    # Create and manage builds
    build = client.create_build(project_id=PROJECT_ID)
    
    # Share builds
    share_url = client.share_build(build.build_id)
    client.stop_sharing_build(build.build_id)
    
    # List builds
    builds = client.list_builds(project_id=PROJECT_ID)
    
    # Get build info
    build_info = client.get_build(build.build_id)
```

## Features

- Synchronous and asynchronous APIs
- Project management (CRUD operations)
- Token management
- Trust policy configuration
- BuildKit endpoint creation and management
- Build sharing and monitoring
- [Python bindings](https://github.com/fal-ai/depot-client/tree/main/depot_client/api) for [depot's gRPC](https://buf.build/depot/api)

## API Reference

### Project Methods

- `list_projects()`: List all available projects
- `create_project(name, region_id)`: Create a new project
- `update_project(project_id, name, region_id)`: Update project details
- `delete_project(project_id)`: Delete a project
- `reset_project(project_id)`: Reset project state

### Token Methods

- `list_tokens(project_id)`: List project tokens
- `create_token(project_id, description)`: Create new token
- `update_token(token_id, description)`: Update token
- `delete_token(token_id)`: Delete token

### Trust Policy Methods

- `list_trust_policies(project_id)`: List trust policies
- `add_trust_policy(project_id, ...)`: Add trust policy
- `remove_trust_policy(project_id, trust_policy_id)`: Remove trust policy

### Build Methods

- `create_build(project_id)`: Create new build
- `finish_build(build_id, error=None)`: Complete build
- `share_build(build_id)`: Share build
- `stop_sharing_build(build_id)`: Stop sharing
- `get_build(build_id)`: Get build info
- `list_builds(project_id)`: List project builds

### Environment Variables

- `DEPOT_API_TOKEN`: Your Depot API token for authentication

## Development

```bash
# Install development dependencies
pip install -e ".[test]"

# Run tests
pytest

# Build package
make build

# Generate API bindings
make protos
make api
```

## License

Apache License 2.0
