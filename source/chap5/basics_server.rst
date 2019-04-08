Device server: Broadcast - Unicast
==================================

In Karabo messages can be of different type with respect to the target, the so-called
**slotInstanceId**. Messages can be either targeted to a single device or all
devices. If all devices are targeted, we refer to so-called broadcast messages.
In the middlelayer API the device server will subscribe for all broadcast messages and
distribute incoming broadcasts to the device children.
This removes unnecessary messaging overhead and will give a performance boost.

Device server: Eventloop
========================

Karabo middlelayer uses Python's asyncio, installing a custom event loop.
All devices in a device server share the **same event loop** which is run in a
single thread. Hence, every blocking call in any device instance results in
blocking every other device in the same device server.
However, the device developer is free to start threads using background, which
starts a thread if used with a function which is not a coroutine.
The event loop thread pool executor can have 200 threads.

Device server: TimeMiXin
========================

The middlelayer device server automatically connects and reconnects to a
TimeServer if the **timeServerId** is provided on initialization.
On updates of the TimeServer a singleton-like TimeMixin class is updated with
a reference timestamp to calculate the trainId's.
Each device will always calculate the trainId automatically if the device
server was once connected to a TimeServer.

Autostarting Devices
====================

A server can automatically launch any number of devices upon starting.
This is done by specifying the ``init`` flag:

.. code-block:: bash

   karabo-middlelayerserver init=$INIT_ARGS

where ``$INIT_ARGS`` is a JSON string of the following format:

.. code-block:: bash

    INIT_ARGS='{"DeviceInstanceId": {"classId": "MyDevice", "parameter": 2, "otherParameter": "['a', 'b', 'c']"}}'

This will launch a device of type ``MyDevice`` with the id
``DeviceInstanceId``, and other parameters.
Mandatory parameters must be specified, else the server will start, but not the
device.
Note how the dictionary is surrounded by single quotes.

Multiple devices can be added:

.. code-block:: bash

    INIT_ARGS='{"Device1": {"classId": "MyDevice", "parameter": 2, "otherParameter": "['a', 'b', 'c']"}
               "GENERATOR": {"classId": "DataGenerator", "autostart": "True"}}'

    karabo-middlelayerserver init=$INIT_ARGS

The deployment_ shows examples of middlelayer servers starting the projectDB
device.

.. _deployment: https://git.xfel.eu/gitlab/Karabo/deployment/merge_requests/827/diffs


