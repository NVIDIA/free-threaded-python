Free-threaded Python
====================


What is that?
-------------

Using this repository, you can build and test a free-threaded Python environment.

Python Steering Commitee approved `PEP 703 <https://peps.python.org/pep-0703/>`_, which removes the `Global Interpreter Lock <https://wiki.python.org/moin/GlobalInterpreterLock>`_ from Python. First Python release that allows for a parallel execution is 3.13 (scheduled October 2024). However, for yet some time you won't be able to ``pip install`` your faviourite extensions and libraries.

Provided Docker allows you to try the free-threaded environment yourself. We've included build routines to some popular extensions (`"My library is missing"`_). Should you encounter any bugs or problems, please let us know in the Issues.

Please note: `This is an experimental software!`_

How to try it?
--------------

#. Clone the repository::

    $ git clone https://github.com/NVIDIA/free-threaded-python.git
    $ cd free-threaded-python

#. Build free-threaded Python environement::

    $ docker build -t free-threaded-python .

#. Try it::

   $ docker run -it --gpus all -v test:/test free-threaded-python python3 /test/simple.py

#. If you want to build the container with PyTorch, specify the target (this takes some time)::

   $ docker build -t free-threaded-python --target pytorch .


This is an experimental software!
---------------------------------

Removing GIL is a breaking change for many Python extensions and it will take years to adjust the ecosystem fully to the parallel execution. Moreover, this will not be possible without the community. **Please keep in mind, that by no means this is a production-ready software**. However, should you run into any bugs, please let us know in the Issues. Contributions and Pull Requests are also welcome.

"My library is missing"
-----------------------

It's not our intention to recreate whole Python ecosystem. However, if you are using a Python library which is missing here, please let us know in the Issues. Although we focus mostly on NVIDIA Python ecosystem, we'll do our best to include the most popular extensions in this environment configuration.
