# Backup tool for github repos

This backup tool is scanning your github account and is creating and maintaining a local copy of all your github repositories as an on prem backup.

## Local development

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and Git.
The Docker image uses Python 3.11; uv can install it if it is not available locally.
From the project directory, run:

```shell
uv python install 3.11
uv sync --python 3.11
cp .env.sample .env
```

Edit `.env` with your GitHub username and token (`GITHUBUSER` and
`GITHUBKEY`) and MQTT connection settings (`MQTTSERVER`, `MQTTPORT`,
`MQTTUSER`, and `MQTTPWD`). The MQTT broker must be reachable from your host,
not just from the Docker network. The script reads `.env` automatically;
environment variables override values in that file. Do not commit credentials.

Run the backup with a local destination (this contacts GitHub and modifies
the destination):

```shell
uv run python github_backup.py --path /path/to/backups --verbose
```

Choose a separate destination for development to avoid changing existing
backups. The script currently prints clone URLs containing the GitHub token;
treat its terminal output as sensitive. For editor support, select
`.venv/bin/python` as the Python interpreter. Dependencies for local development
are in `pyproject.toml` and `uv.lock`; the Docker image continues to use
`requirements.txt`, so keep both dependency lists in sync when changing them.

## Usage

## How to start in test mode
```shell
source .env
docker run --name githubbackup -v "$BACKUPDIR:/backup_path:delegated" --env-file .env --user 1000 --network $NETWORK githubbackup:latest 
```

## How to start in debug mode

In debug mode you end up on a command line and can play around with the container, start the script and so on.

```shell
source .env
docker run --name githubbackup -v "$BACKUPDIR:/backup_path:delegated" --env-file .env --user 1000 --network $NETWORK -it githubbackup:latest /bin/sh
```
