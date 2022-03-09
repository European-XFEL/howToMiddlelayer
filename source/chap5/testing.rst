.. _device_testing

Device Testing
==============

Device Context
--------------

**This is only available with Karabo Version >= 2.15.X**

The :class:`AsyncDeviceContext` is an asynchronous context manager to handle
device instances. If can be fairly straightforward used with :module:`pytest`.

.. literalinclude:: code/context_example.py
   :language: python
