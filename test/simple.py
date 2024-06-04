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

import math
import time
import threading

doc = """
This is a simple test of free-threaded Python environment. It runs a computationally heavy-ish 
task on alternating number of CPU threads. In a free-threaded environment, the execution times 
of the runs shall be similar.
"""


def computational_heavy(iterations):
    val = 0
    sin = math.sin
    cos = math.cos
    for i in range(1, iterations):
        val += sin(i) * cos(i)
    return val


def test(thread_id, iterations=1000000):
    computational_heavy(iterations)


print(doc)

num_threads = [2, 18, 2, 18, 2, 18]

for nt in num_threads:
    threads = [
        threading.Thread(target=test, name=f"Thread{i}", args=(i,)) for i in range(nt)
    ]
    start = time.perf_counter_ns()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    stop = time.perf_counter_ns()
    print(f"{nt=}.\tElapsed time {stop-start} ns")
