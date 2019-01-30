**********************
Karabo middlelayer API
**********************

The Karabo ``middlelayer`` API is written in pure `Python <http://www.python.org>`_
deriving its name from the main design aspect: controlling and monitoring
driver devices while providing state aggregation and additional functionality.
The same interface is also used for the macros.
Hence, this api exposes an efficient interface for tasks such as
interacting with other devices via device proxies to enable monitoring of properties,
executing commands and waiting on their completion, either synchronously
or asynchronously.

.. include:: basic_device.rst
.. include:: code_style.rst
.. include:: slots.rst
.. include:: device_attributes.rst
.. include:: node.rst
.. include:: error_handling.rst
