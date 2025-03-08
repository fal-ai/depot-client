from depot_client import Client, AsyncClient
import aiofiles
import os
import asyncio
import subprocess
import pytest

PROJECT_ID = "749dxclhrj"

DOCKERFILE_1 = """
FROM alpine:3.8
RUN echo "Hello, World!"
"""

DOCKERFILE_2 = """
FROM ubuntu:18.04
RUN echo "Hello, World!"
"""

DOCKERFILE_3 = """
FROM fedora:30
RUN echo "Hello, World!"
"""

@pytest.mark.parametrize("dockerfile", [DOCKERFILE_1, DOCKERFILE_2, DOCKERFILE_3])
def test_e2e(dockerfile, tmp_path):
    with open(tmp_path / "Dockerfile", "w") as f:
        f.write(dockerfile)

    with Client() as client:
        with client.create_endpoint(PROJECT_ID) as endpoint:
            cert_path = os.path.join(tmp_path, "tls.crt")
            key_path = os.path.join(tmp_path, "tls.key")
            ca_cert_path = os.path.join(tmp_path, "ca.crt")

            with open(ca_cert_path, "w", encoding="utf-8") as f:
                f.write(endpoint.ca_cert)

            with open(cert_path, "w", encoding="utf-8") as f:
                f.write(endpoint.cert)

            with open(key_path, "w", encoding="utf-8") as f:
                f.write(endpoint.key)

            cmd = [
                "buildctl",
                "--addr", endpoint.endpoint,
                "--tlscacert", ca_cert_path,
                "--tlscert", cert_path,
                "--tlskey", key_path,
                "build",
                "--frontend=dockerfile.v0",
                f"--local=context={tmp_path}",
                f"--local=dockerfile={tmp_path}",
                "--output",
                f"type=image,image-manifest=true,compression=estargz,force-compression=true,oci-mediatypes=true",
            ]
            subprocess.check_call(cmd)


@pytest.mark.parametrize("dockerfile", [DOCKERFILE_1, DOCKERFILE_2, DOCKERFILE_3])
async def test_e2e_async(dockerfile, tmp_path):
    with open(tmp_path / "Dockerfile", "w") as f:
        f.write(dockerfile)

    async with AsyncClient() as client:
        async with client.create_endpoint(PROJECT_ID) as endpoint:
            cert_path = os.path.join(tmp_path, "tls.crt")
            key_path = os.path.join(tmp_path, "tls.key")
            ca_cert_path = os.path.join(tmp_path, "ca.crt")

            async with aiofiles.open(ca_cert_path, "w", encoding="utf-8") as f:
                await f.write(endpoint.ca_cert)

            async with aiofiles.open(cert_path, "w", encoding="utf-8") as f:
                await f.write(endpoint.cert)

            async with aiofiles.open(key_path, "w", encoding="utf-8") as f:
                await f.write(endpoint.key)


            cmd = [
                "buildctl",
                "--addr", endpoint.endpoint,
                "--tlscacert", ca_cert_path,
                "--tlscert", cert_path,
                "--tlskey", key_path,
                "build",
                "--frontend=dockerfile.v0",
                f"--local=context={tmp_path}",
                f"--local=dockerfile={tmp_path}",
                "--output",
                f"type=image,image-manifest=true,compression=estargz,force-compression=true,oci-mediatypes=true",
            ]
            proc = await asyncio.create_subprocess_exec(*cmd)
            await proc.wait()
            assert proc.returncode == 0
