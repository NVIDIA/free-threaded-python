# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

ARG CUDA_VERSION=12.4.0

FROM nvcr.io/nvidia/cuda:${CUDA_VERSION}-devel-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive
ENV PYTHON_GIL=0

# Install build tools
RUN apt update && \
    apt install -y wget autoconf autogen git pkg-config libbz2-dev liblzma-dev libgdbm-dev     \
                   libsqlite3-dev uuid-dev libreadline-dev libssl-dev zlib1g-dev               \
                   libncurses5-dev libncursesw5-dev libffi-dev libdb-dev zip build-essential   \
                   autoconf autogen unzip libboost-all-dev gdb vim tree ack cmake pre-commit   \
                   shellcheck git-lfs patchelf gawk software-properties-common lsb-release     \
                   libtiff-dev libzstd-dev libopencv-dev libclang-dev

WORKDIR /opt

# Build and install the latest CPython
RUN git clone -b 3.13 --single-branch --recursive -j"$(grep ^processor /proc/cpuinfo | wc -l)" https://github.com/python/cpython.git && cd cpython && \
    mkdir build && cd build && ../configure --disable-gil && \
    make -j"$(grep ^processor /proc/cpuinfo | wc -l)" install

RUN update-alternatives --install /usr/bin/python python $(which python3.13) 0 && \
    update-alternatives --force --install /usr/bin/pip pip $(which pip3.13) 0

# General build dependencies
RUN pip install setuptools wheel clang==14 libclang==14.0.1

# Numpy provides 3.13t wheels
RUN pip install numpy

# Cython and Pillow nightly builds
RUN python3 -m pip install -i https://pypi.anaconda.org/scientific-python-nightly-wheels/simple cython pillow

# PyTorch nightly build
RUN if [ "$(echo "$CUDA_VERSION" | tr -d . | head -c 3)" != 124 ]; then \
        echo "No available free-threaded PyTorch wheels for CUDA version $CUDA_VERSION"; \
    else \
        python3 -m pip install --pre torch --index-url https://download.pytorch.org/whl/nightly/cu124; \
    fi

# nvImageCodec provides 3.13t wheels
RUN suffix="$(echo "$CUDA_VERSION" | tr -d . | head -c 2)" && \
    if ! echo "$suffix" | grep -wq -e 11 -e 12; then \
        echo "No available nvImageCodec wheels for CUDA version $CUDA_VERSION"; \
    else \
        python3 -m pip install nvidia-nvimgcodec-cu$suffix; \
    fi

ARG CUDA_ARCHS='60;70;80;90'

# Install CV-CUDA from source
# Clone and patch
RUN git clone -b v0.8.0-beta https://github.com/CVCUDA/CV-CUDA.git && \
    cd CV-CUDA && sed -i 's/skip_precommit=0/skip_precommit=1/g' init_repo.sh && \
    ./init_repo.sh && cd 3rdparty/pybind11 && git submodule update --init . && git checkout v2.13.6
# Build and install
RUN cd CV-CUDA && \
    CUDA_MAJOR=12 ci/build.sh release build -DCMAKE_CUDA_ARCHITECTURES="$CUDA_ARCHS" && \
    python3 -m pip install build/python3.13/wheel

# Install NVTX from source
RUN git clone -b release-v3 https://github.com/NVIDIA/NVTX.git && cd NVTX/python && \
    sed -Ei 's/"Cython"/"Cython==3.0.5"/' pyproject.toml && \
    sed -Ei 's;(include_dirs\s*=.+,)];\1 "/opt\/NVTX\/c\/include"];' setup.py && \
    python3 -m pip install .

# Install cuDNN FE
RUN apt install -y cudnn && export CUDNN_INCLUDE_DIR=/usr/include && \
    python3 -m pip install git+https://github.com/NVIDIA/cudnn-frontend.git

# Install CUDA-Python
RUN git clone -b "v$CUDA_VERSION" https://github.com/NVIDIA/cuda-python && cd cuda-python && \
    python3 -m pip install -r requirements.txt && export CUDA_HOME=/usr/local/cuda && \
    PARALLEL_LEVEL="$(grep ^processor /proc/cpuinfo | wc -l)" python3 setup.py bdist_wheel install && \
    python3 -m pip install dist/*.whl
# Install cuda.core
RUN cd cuda-python && git switch main && \
    cd cuda_core && python3 -m pip install --no-build-isolation .

# Install Warp
RUN git clone https://github.com/NVIDIA/warp.git && cd warp && \
    python3 build_lib.py && python3 -m pip install .

# Install Nsight Systems
RUN wget -O nsight.deb https://developer.nvidia.com/downloads/assets/tools/secure/nsight-systems/2023_4_1_97/nsightsystems-linux-cli-public-2023.4.1.97-3355750.deb/ && \
    dpkg -i nsight.deb

RUN rm -r /opt/nvidia/entrypoint.d/*
COPY entrypoint.d /opt/nvidia/entrypoint.d
