# C++ Development Environment for ariane-xml with Jupyter support
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

# Build the Ariane-XML C++ project
RUN cd ariane-xml-c-kernel && mkdir -p build && cd build && cmake .. && make

# Install Jupyter and the Ariane-XML kernel
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

# Install the Ariane-XML kernel package (setup.py is in ariane-xml-jupyter-kernel/)
RUN pip3 install -e ./ariane-xml-jupyter-kernel

# Install the kernel spec
RUN python3 -m ariane_xml_jupyter_kernel.install

# Install the Ariane-XML encryption module (setup.py is in ariane-xml-crypto/)
RUN pip3 install -e ./ariane-xml-crypto

# Expose Jupyter port
EXPOSE 8888

CMD ["/bin/bash"]
