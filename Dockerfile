ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-slim AS base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Create a non-privileged user that the app will run under.
# See https://docs.docker.com/go/dockerfile-user-best-practices/
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a cache mount to /root/.cache/pip to speed up subsequent builds.
# Leverage a bind mount to requirements.txt to avoid having to copy them into
# into this layer.
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

RUN apt-get update && apt-get install -y wget
RUN chown appuser:appuser /app

# Switch to the non-privileged user to run the application.
USER appuser

RUN wget https://github.com/windtf/wireproxy/releases/download/v1.1.3/wireproxy_linux_amd64.tar.gz
RUN tar xzvf wireproxy_linux_amd64.tar.gz && rm wireproxy_linux_amd64.tar.gz

# Copy the source code into the container.
COPY src/ src/
COPY ca.rsa.4096.crt ca.rsa.4096.crt

# Run the application.
CMD python3 src/pia_wireproxy.py
