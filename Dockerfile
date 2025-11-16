# C++ Development Environment for expocli with Jupyter support
FROM ubuntu:22.04

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

# Install build essentials, C++ dependencies, and Python
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    wget \
    libpugixml-dev \
    libreadline-dev \
    gdb \
    valgrind \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Build the ExpoCLI C++ project
RUN mkdir -p build && cd build && cmake .. && make

# Install Jupyter and the ExpoCLI kernel
RUN pip3 install --no-cache-dir \
    jupyterlab \
    notebook \
    ipykernel \
    jupyter-client

# Install encryption module dependencies
RUN pip3 install --no-cache-dir \
    cryptography \
    pyyaml \
    faker \
    lxml \
    ff3

# Install the ExpoCLI kernel package (setup.py is in expocli_kernel/)
RUN pip3 install -e ./expocli_kernel

# Install the kernel spec
RUN python3 -m expocli_kernel.install

# Install the ExpoCLI encryption module (setup.py is in expocli_crypto/)
RUN pip3 install -e ./expocli_crypto

# Expose Jupyter port
EXPOSE 8888

CMD ["/bin/bash"]
