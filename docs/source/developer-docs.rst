Developer Documentation
===========================

.. toctree::
   :maxdepth: 2

System Overview
^^^^^^^^^^^^^^^

The standard Jupyter notebook has three components, (1) the client that makes up the notebook cells, (2) a web server that lists notebook files, directories and serves notebook assets like HTML and CSS (3) a kernel that executes commands in the chosen language (in our case Python).

.. figure:: https://docs.google.com/drawings/d/1Zss2O5rXANNYnaooZhnKhWCVu6wjURmBWNeKLL_QXXc/pub?w=960&h=720
   :align: center

   Components of the Jupyter Notebook

When you execute python in a Jupyter Notebook cell the python code was transmitted (as a string) over a web socket to the webserver, then proxied through ZeroMQ to the IPykernel where it was evaluated as a Python expression. The results of that execution are then sent back over the ZeroMQ/Websocket connection and displayed in your browser. This is the standard way in which Jupyter notebook takes code from a web browser, and executes it in an interactive shell (kernel) and returns the output.


*TODO introduce comm channels*

.. figure:: https://docs.google.com/drawings/d/1WwUg_nUWkPTsTYTE9Bnjnzu-sIoZh4_PxM4jW7hONiU/pub?w=960&h=720
   :align: center

   Kernel/Map communication


*TODO: discuss RPC mechanism*

*TODO: introduce visualisation mechanisms*

.. figure:: https://docs.google.com/drawings/d/1l0183Bo6WxjQOOixpMmKyOSlT8t2B9fepKtP_kIzmVc/pub?w=960&h=720
   :align: center

   Data visualization with KTile

*TODO: pointers to KTile/TileStache documentation*

.. figure:: https://docs.google.com/drawings/d/1FN9jgYv2BlUcQ5GOzltmszP6ZG16mHtqthJj-Yi0pyk/pub?w=960&h=720
   :align: center

   GeoNotebook System Detail

.. _automated-testing:

Automated Testing
^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # From the source root
   pip install -r requirements-dev.txt
   tox

   # Optionally only run tests on python 2.7
   # tox -e py27


Developer Cookbook
^^^^^^^^^^^^^^^^^^

Adding an RPC Call
##################

Server Side
$$$$$$$$$$$

Client Side
$$$$$$$$$$$
