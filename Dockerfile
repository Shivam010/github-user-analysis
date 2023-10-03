FROM python:3.10.4-slim-bullseye as builder

# Extra python env
ENV PYTHONDONTWRITEBYTECODE=0
ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV GITHUB_ACCESS_TOKEN=ghp_xxxxxx

# Mount Directory
ENV MOUNT_DIRECTORY=/guadata

# install requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

# our internal package and main.py file
COPY internal internal
COPY main.py main.py

# default docker port to expose, '-p' flag is used
EXPOSE 8000

ENTRYPOINT [ "/usr/local/bin/gunicorn", "-w=4", "main:app", "-b=0.0.0.0:8000" ]
