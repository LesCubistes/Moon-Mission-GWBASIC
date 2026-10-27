FROM ubuntu:24.04
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    gcc libc6-dev dosbox xvfb xauth x11-xserver-utils xdotool tesseract-ocr python3 python3-pil python3-pip python3-venv mtools nasm ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*
RUN python3 -m venv --system-site-packages /opt/ci && /opt/ci/bin/pip install --no-cache-dir pcbasic==2.0.8
ENV PATH="/opt/ci/bin:${PATH}"
WORKDIR /workspace
