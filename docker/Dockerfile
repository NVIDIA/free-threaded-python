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

FROM nvcr.io/nvidia/cuda:12.5.0-devel-ubuntu22.04 as base

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
    mkdir build && cd build && ../configure --disable-gil --with-pydebug && \
    make -j"$(grep ^processor /proc/cpuinfo | wc -l)" install

# Install numpy from source
# Clone and patch
RUN git clone -b v1.26.4 --recursive -j"$(grep ^processor /proc/cpuinfo | wc -l)" https://github.com/numpy/numpy.git && cd numpy && \
    sed -Ei 's/importlib.resources.read_text\((.+),\s*(.+),\s*encoding\s*=\s*(.+)\)/importlib.resources.files(\1)\.joinpath(\2).read_text(encoding=\3)/' vendored-meson/meson/mesonbuild/dependencies/cmake.py && \
    sed -Ei 's/(\s+)"Cython>=[^"]+",/\1"Cython==3.0.5",\n\1"setuptools>=69.2",/' pyproject.toml && \
    sed -i 's/#define PyArray_REFCOUNT(obj).*/#define PyArray_REFCOUNT Py_REFCNT/' numpy/core/include/numpy/ndarrayobject.h
# Build
RUN cd numpy && python3 -m pip install .

# Install nvImageCodec from source
# Build dependencies
RUN python3 -m pip install setuptools wheel clang==14 libclang==14.0.1
# Clone and patch
RUN git clone --recursive --depth 1 -j"$(grep ^processor /proc/cpuinfo | wc -l)" https://github.com/NVIDIA/nvImageCodec.git && cd nvImageCodec && \
    sed -Ei 's/(, )?<=3.12//' python/setup.py.in && \
    sed -i 's/set\s*(PYTHON_VERSIONS\s*".*")/set(PYTHON_VERSIONS "3.13")/' cmake/Utils.cmake && \
    cd external/pybind11 && git remote add colesbury https://github.com/colesbury/pybind11.git && \
    git fetch colesbury && git checkout colesbury/v2.11.1-nogil && \
    sed -i 's/Py_NOGIL/Py_GIL_DISABLED/g' include/pybind11/detail/internals.h
# Build and install
RUN mkdir -p nvImageCodec/build && cd nvImageCodec/build && \
    WHL_OUTDIR=/tmp ../docker/build_helper.sh && \
    apt install -y /tmp/*.deb && python3 -m pip install /tmp/*.whl

ARG CUDA_ARCHS

# Install CV-CUDA from source
# Clone and patch
RUN git clone https://github.com/CVCUDA/CV-CUDA.git && \
    cd CV-CUDA && sed -i 's/skip_precommit=0/skip_precommit=1/g' init_repo.sh && \
    ./init_repo.sh && cd 3rdparty/pybind11 && \
    git remote add colesbury https://github.com/colesbury/pybind11.git && git fetch colesbury && \
    git checkout colesbury/v2.11.1-nogil && sed -i 's/Py_NOGIL/Py_GIL_DISABLED/g' include/pybind11/detail/internals.h
# Build and install
RUN cd CV-CUDA && \
    CUDA_MAJOR=12 ci/build.sh release build -DCMAKE_CUDA_ARCHITECTURES="$CUDA_ARCHS" && \
    python3 -m pip install build/python3.13/wheel

# Install NVTX from source
RUN git clone -b release-v3 https://github.com/NVIDIA/NVTX.git && cd NVTX/python && \
    sed -Ei 's/"Cython"/"Cython==3.0.5"/' pyproject.toml && \
    sed -Ei 's;(include_dirs\s*=.+,)];\1 "/opt\/NVTX\/c\/include"];' setup.py && \
    python3 -m pip install .

# Install Python dependencies
RUN python3 -m pip install more_itertools

# Install Nsight Systems
RUN wget -O nsight.deb https://developer.nvidia.com/downloads/assets/tools/secure/nsight-systems/2023_4_1_97/nsightsystems-linux-cli-public-2023.4.1.97-3355750.deb/ && \
    dpkg -i nsight.deb
