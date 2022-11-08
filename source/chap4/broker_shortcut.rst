Broker Shortcut
===============

Karabo devices are hosted on device servers. In to communicate, messages are send via
the broker to either reconfigure other devices or call device slots.

However, it is possible to directly communicate and control devices on the same
devices server via **getLocalDevice**.

This is available with **Karabo 2.15.X**

.. literalinclude:: code/broker_shortcut.py
   :language: python
