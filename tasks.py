import os
import shutil

try:
    from dotenv import load_dotenv
except ImportError as e:
    raise ImportError(
        "Please install dotenv: `pip install -U python-dotenv`"
    ) from e
try:
    from invoke import task
except ImportError as e:
    raise ImportError(
        "Please install invoke: `pip install invoke`"
    ) from e

# Load the environment variables from .env file
load_dotenv()

# Get the mode from the environment (dev or prod)
DOCKER_MODE = os.getenv('DOCKER_MODE', 'dev')

# Docker Compose files based on mode
# DOCKER_COMPOSE_FILE = "common.yml "
DOCKER_COMPOSE_FILE = "local.yml" if DOCKER_MODE == "dev" else "production.yml"

WEB_CONTAINER_NAME = f"{os.getenv('PROJECT_NAME')}_web"


# Determine whether to use 'docker-compose' or 'docker compose'
DOCKER_COMPOSE_CMD = (
    f"{shutil.which('docker')} compose" or shutil.which("docker-compose")
)

@task
def build(c):
    """Build Docker containers"""
    cmd = f"{DOCKER_COMPOSE_CMD} -f {DOCKER_COMPOSE_FILE} build"
    c.run(cmd, pty=True)

@task
def start(c, detach=True):
    """Start Docker containers"""
    cmd = f"{DOCKER_COMPOSE_CMD} -f {DOCKER_COMPOSE_FILE} up"
    if detach:
        cmd = f"{cmd} -d"
    c.run(cmd, pty=True)

@task
def stop(c, s=None, remove_volumes=False):
    """Stop Docker containers"""
    cmd = f"{DOCKER_COMPOSE_CMD} -f {DOCKER_COMPOSE_FILE} down"
    if s:
        cmd = f"{cmd} {s}"
    if remove_volumes:
        cmd = f"{cmd} -v"
    c.run(cmd, pty=True)

@task
def restart(c, s=None):
    """Restart Docker containers"""
    cmd = f"{DOCKER_COMPOSE_CMD} -f {DOCKER_COMPOSE_FILE} restart"
    if s:
        cmd = f"{cmd} {s}"
    c.run(cmd, pty=True)

@task
def update(c):
    """Update Docker containers"""
    stop(c)
    build(c)
    start(c)

@task(help={
    'tail': 'Number of lines to show from the end of the logs',
    'follow': 'Follow the logs',
    'container': 'Container name',
})
def logs(c, tail=10, follow=True, container=None):
    """Show logs of Docker containers"""
    cmd = f"{DOCKER_COMPOSE_CMD} -f {DOCKER_COMPOSE_FILE} logs"
    if container:
        cmd = f"{cmd} {container}"
    if follow:
        cmd = f"{cmd} -f"
    if tail:
        cmd = f"{cmd} --tail {tail}"
    c.run(cmd, pty=True)

@task
def shell(c):
    """Open a shell in the web container"""
    cmd = f"docker exec -it {WEB_CONTAINER_NAME} sh"
    c.run(cmd, pty=True)
