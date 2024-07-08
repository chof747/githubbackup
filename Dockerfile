FROM alpine:latest

RUN apk add git
RUN apk add --no-cache python3 py3-pip python3-dev build-base


WORKDIR /app
COPY . /app

RUN python3 -m venv /app/venv
RUN . /app/venv/bin/activate && pip install --upgrade pip
RUN . /app/venv/bin/activate && pip install -r requirements.txt

CMD ["/app/venv/bin/python3", "github_backup.py", "-p", "/backup_path", "-v"]