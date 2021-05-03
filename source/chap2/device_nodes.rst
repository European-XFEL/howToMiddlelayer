.. _device-nodes

Device Nodes
=====================================

Next to use :func:`connectDevice` or :func:`getDevice` it is possible in
middle layer device development to use a  :class:`DeviceNode`.

.. note::
    DeviceNodes are **MANDATORY** properties and can only be set before
    instantiation, e.g. are **INITONLY**!

In contrast to a regular ``Access.MANDATORY`` definition, a ``DeviceNode`` also does not
accept an empty string.
Defining a remote device is done as follows:

.. code-block:: Python

    motor1Proxy = DeviceNode(displayedName="RemoteDevice",
                             description="Remote motor 1")

    motor2Proxy = DeviceNode(displayedName="RemoteDevice",
                             description="Remote motor 2")

    motor3Proxy = DeviceNode(displayedName="RemoteDevice",
                             description="Remote motor 3")

However, a ``DeviceNode`` must connect within a certain timeout (default is 2 seconds )
to the configured remote device, otherwise the device holding a ``DeviceNode`` shuts itself down.

Accessing, setting, and waiting for updates from :class:`DeviceNode` is similar
to what was done previously.

Monitoring the position of these three motors is done so:

.. code-block:: Python

    positions_list = [dev.position for dev in [motor1Proxy,
                                               motor2Proxy,
                                               motor3Proxy]]
    await waitUntilNew(*positions_list)

Setting a parameter is a simple assignment but calling a function needs
to be **awaited**:

.. code-block:: Python

    self.motor1Proxy.targetPosition = 42
    await self.motor1Proxy.move()

Doing so for several devices is done using :func:`gather`:

.. code-block:: Python

    async def moveSeveral(self, positions):
        futures = []

        for device, position in zip(self.devices, positions):
            await setWait(device, targetPosition=position)
            futures.append(device.move())

        await gather(*futures)

Function and parameter calls are now exactly as they were when using
:func:`getDevice` or :func:`connectDevice`, but now details regarding the
connection to remote devices are left to the middle layer API.

Timeout parameter
*****************

The ``DeviceNode`` holds a proxy to a remote device. During initialization, the
DeviceNodes try to establish a proxy connection. Once connected, the deviceId of the
remote device can be represented, but internally the proxy is retrieved. For this,
a connection must be established. If this cannot be guaranteed within a certain time,
the device holding the device nodes will shut itself down.

A timeout parameter of up to 5 seconds can be provided.

.. code-block:: Python

    motor1Proxy = DeviceNode(displayedName="RemoteDevice",
                             description="Remote motor 1",
                             timeout=4.5)

Reference Implementations
-------------------------
The following devices implement the functionalities described above in a working
environment, and can be considered reference implementations:

* `fastValve`_ is a middle layer device interfacing with several remote devices
   through the use of :class:`DeviceNode`

.. _fastValve: http://in.xfel.eu/gitlab/karaboDevices/fastValve
