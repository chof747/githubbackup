FROM python:3.11-alpine AS build

RUN apk add --no-cache build-base git

WORKDIR /build

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN python -m pip install --upgrade pip setuptools wheel \
    && python -m pip install --no-cache-dir -r requirements.txt

COPY github_backup.py .


FROM python:3.11-alpine AS runtime

RUN apk add --no-cache ca-certificates git

WORKDIR /app

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

COPY --from=build /opt/venv /opt/venv
COPY --from=build /build/github_backup.py .

CMD ["python", "github_backup.py", "-p", "/backup_path", "-v"]
