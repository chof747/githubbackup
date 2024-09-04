Backup tool for github repos

# Useage

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