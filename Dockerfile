FROM alpine:latest

RUN apk add git
RUN apk add --no-cache python3 py3-pip
#RUN apk add pip

WORKDIR /app
COPY . /app

RUN pip3 install .

CMD [ "github_backup", "-p", "/backup_path"]
