#!/bin/bash -e

# Copyright (c) 2025, NVIDIA CORPORATION & AFFILIATES. All rights reserved.

# PYTHON_VERSION variable
[[ "$PYTHON_VERSION" =~ ^3\.([0-9]+)$ ]] || { echo "PYTHON_VERSION must be in format '3.minor'"; exit 1; }
minor=${BASH_REMATCH[1]}
if (( minor > 13 )); then
    echo "Maximum supported Python version is 3.13 (got $PYTHON_VERSION)"
    exit 1
fi

# ENABLE_GIL variable check
[[ "$ENABLE_GIL" =~ ^[01]$ ]] || { echo "ENABLE_GIL must be 0 or 1 (got '$ENABLE_GIL')"; exit 1; }
if (( ENABLE_GIL == 0 )) && (( minor != 13 )); then
    echo "ENABLE_GIL=0 is only supported with Python 3.13 (got $PYTHON_VERSION)"
    exit 1
fi
