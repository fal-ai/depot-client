# depot-client

Python client library for [Depot](https://depot.dev). Provides both synchronous and asynchronous APIs through an intuitive Pythonic interface.

## Installation

```bash
pip install depot-client
```

## Usage

### Basic Example

```python
from depot_client import Client

with Client(token=DEPOT_API_TOKEN) as client:
    # Create a project
    project = client.create_project(
        name="my-project",
        region_id="us-east-1"
    )
    
    # Create a build
    with client.create_endpoint(project_id=project.project_id) as endpoint:
        # Write certificates to files
        with open("client.crt", "w") as f:
            f.write(endpoint.cert)
        with open("client.key", "w") as f:
            f.write(endpoint.key)
        with open("ca.crt", "w") as f:
            f.write(endpoint.ca_cert)

        # Use with buildctl:
        # buildctl --addr endpoint.endpoint \
        #     --tlsservername endpoint.server_name \
        #     --tlscacert ca.crt \
        #     --tlscert client.crt \
        #     --tlskey client.key \
        #     build --frontend dockerfile.v0
```

### Async Support

The library provides async versions of all operations:

```python
from depot_client import AsyncClient
import aiofiles

async with AsyncClient(token=DEPOT_API_TOKEN) as client:
    async with await client.create_endpoint(project_id=PROJECT_ID) as endpoint:
        # Write certificates to files
        async with aiofiles.open("client.crt", "w") as f:
            await f.write(endpoint.cert)
        async with aiofiles.open("client.key", "w") as f:
            await f.write(endpoint.key)
        async with aiofiles.open("ca.crt", "w") as f:
            await f.write(endpoint.ca_cert)

        # Use with buildctl:
        # buildctl --addr endpoint.endpoint \
        #     --tlsservername endpoint.server_name \
        #     --tlscacert ca.crt \
        #     --tlscert client.crt \
        #     --tlskey client.key \
        #     build --frontend dockerfile.v0
```

### Project Operations

```python
# List projects
projects = client.list_projects()

# Create and manage tokens
token = client.create_token(
    project_id=project.project_id,
    description="CI/CD token"
)

# Configure trust policies
policy = client.add_trust_policy(
    project_id=project.project_id,
    github={
        "repository_owner": "org",
        "repository": "repo"
    }
)
```

### Build Operations

```python
# Create and track builds
build = client.create_build(project_id=PROJECT_ID)

# Get a shareable URL for the build
share_url = client.share_build(build.build_id)

# List project builds
builds = client.list_builds(project_id=PROJECT_ID)
```

## Features

- Pythonic interface to Depot's API
- Context manager support for proper resource cleanup
- Full async/await support using `AsyncClient`
- Type hints throughout for better IDE integration
- Automatic handling of BuildKit endpoint lifecycle
- Comprehensive error handling

## API Reference

### Client Methods

#### Project Operations
- `list_projects() -> List[ProjectInfo]`: List all available projects
- `create_project(name: str, region_id: str) -> ProjectInfo`: Create a new project
- `get_project(project_id: str) -> ProjectInfo`: Get project details
- `delete_project(project_id: str) -> None`: Delete a project
- `reset_project(project_id: str) -> None`: Reset project state

#### Token Management
- `list_tokens(project_id: str) -> List[TokenInfo]`: List project tokens
- `create_token(project_id: str, description: str) -> TokenCreationInfo`: Create new token
- `update_token(token_id: str, description: str) -> None`: Update token description
- `delete_token(token_id: str) -> None`: Delete token

#### Trust Policies
- `list_trust_policies(project_id: str) -> List[TrustPolicy]`: List trust policies
- `add_trust_policy(project_id: str, github: Optional[dict] = None, circleci: Optional[dict] = None, buildkite: Optional[dict] = None) -> TrustPolicy`: Add trust policy
- `remove_trust_policy(project_id: str, trust_policy_id: str) -> None`: Remove trust policy

#### Build Operations
- `create_build(project_id: str) -> Build`: Create new build
- `finish_build(build_id: str, error: Optional[str] = None) -> None`: Complete build
- `share_build(build_id: str) -> str`: Create a shareable URL for the build
- `stop_sharing_build(build_id: str) -> None`: Revoke the shareable URL for the build
- `get_build(build_id: str) -> BuildInfo`: Get build info
- `list_builds(project_id: str) -> List[BuildInfo]`: List project builds

#### BuildKit Integration
- `create_endpoint(project_id: str, platform: Optional[str] = None) -> Endpoint`: Create a BuildKit endpoint

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